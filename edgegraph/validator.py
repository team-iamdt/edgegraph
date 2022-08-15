import asyncio
import typing as t

import edgedb as e

from edgegraph.errors import ValidatedErrorValue, ValidationError
from edgegraph.schema import EdgeModel


class SchemaValidator:
    _edgedb_dsn: str
    _models: t.Set[t.Type[EdgeModel]]
    _fail_fast: bool
    _check_validation_rules: bool
    _max_concurrency: t.Optional[int]
    _credentials: t.Optional[str]
    _credentials_file: t.Optional[str]
    _tls_ca: t.Optional[str]
    _tls_ca_file: t.Optional[str]
    _tls_security: t.Optional[str]
    _wait_until_available: int
    _timeout: int
    _client: e.AsyncIOClient

    def __init__(
        self,
        edgedb_dsn: str,
        models: t.Set[t.Type[EdgeModel]],
        # EdgeDB Connect Options
        max_concurrency: t.Optional[int] = None,
        credentials: str = None,
        credentials_file: str = None,
        tls_ca: str = None,
        tls_ca_file: str = None,
        tls_security: str = None,
        wait_until_available: int = 30,
        timeout: int = 10,
        # currently those features are not implemented
        fail_fast: bool = False,
        check_validation_rules: bool = False,
    ):
        self._edgedb_dsn = edgedb_dsn
        self._models = models
        self._fail_fast = fail_fast
        self._check_validation_rules = check_validation_rules
        self._max_concurrency = max_concurrency
        self._credentials = credentials
        self._credentials_file = credentials_file
        self._tls_ca = tls_ca
        self._tls_ca_file = tls_ca_file
        self._tls_security = tls_security
        self._wait_until_available = wait_until_available
        self._timeout = timeout
        self._client = e.create_async_client(
            dsn=self._edgedb_dsn,
            max_concurrency=self._max_concurrency,
            credentials=self._credentials,
            credentials_file=self._credentials_file,
            tls_ca=self._tls_ca,
            tls_ca_file=self._tls_ca_file,
            tls_security=self._tls_security,
            wait_until_available=self._wait_until_available,
            timeout=self._timeout,
        )

    async def _inspect_and_validate_outlines(
        self,
        client: e.AsyncIOClient,
    ) -> t.List[ValidatedErrorValue]:
        outline_error_message = "Validation Failure in Outline Inspection."

        # TODO(Hazealign): Migrate to Query Builder when Query Builder implemented
        result: e.Set = await client.query(
            """
                with module schema select ObjectType {
                    name
                } filter
                    .name not like 'cfg::%' and
                    .name not like 'std::%' and
                    .name not like 'sys::%' and
                    .name not like 'std::%' and
                    .name not like 'schema::%' and
                    .abstract = false;
            """
        )

        target: t.List[str] = []
        for model in self._models:
            name = model.__name__ if model.Config.name is None else model.Config.name
            module = model.Config.module
            target.append(f"{module}::{name}")

        origin = [x.name for x in result]
        errors = []

        if len(origin) != len(target):
            errors.append(
                ValidatedErrorValue(
                    error_message=f"{len(origin)} models found in EdgeDB, {len(target)} expected",
                )
            )

            if self._fail_fast:
                raise ValidationError(errors, outline_error_message)

        for item in origin:
            if item not in target:
                errors.append(
                    ValidatedErrorValue(
                        module=item.split("::")[0],
                        type=item.split("::")[1],
                        error_message=f"{item} not found in target",
                    )
                )

                if self._fail_fast:
                    raise ValidationError(errors, outline_error_message)

        if len(errors) > 0:
            raise ValidationError(errors, outline_error_message)

        return errors

    def _check_outline_properties(
        self,
        module: str,
        typ: str,
        result: e.Object,
        schema: t.Dict[str, t.Any],
    ) -> t.List[ValidatedErrorValue]:
        origin = []
        for link in result.links:
            if link.name != "__type__":
                origin.append(link.name)

        for prop in result.properties:
            if prop.name != "__type__":
                origin.append(prop.name)

        target = schema["properties"].keys()
        errors: t.List[ValidatedErrorValue] = []

        if len(origin) != len(target):
            errors.append(
                ValidatedErrorValue(
                    module=module,
                    type=typ,
                    error_message=f"{len(origin)} properties / link found in EdgeDB,"
                    f" {len(target)} expected with local schema.",
                )
            )

        for item in origin:
            if item not in target:
                errors.append(
                    ValidatedErrorValue(
                        module=module,
                        type=typ,
                        property=item,
                        error_message=f"{item} not found in target",
                    )
                )

        return errors

    def _check_is_valid_link(
        self,
        module: str,
        typ: str,
        links: e.Set,
        field: t.Tuple[str, t.Dict[str, t.Any]],
    ) -> t.Optional[ValidatedErrorValue]:
        (field_name, field_info) = field
        if field_name not in [link.name for link in links]:
            return ValidatedErrorValue(
                module=module,
                type=typ,
                property=field_name,
                error_message=f"{field_name} not found in target",
            )

        # check cardinality and type
        for link in links:
            if field_name == link.name:
                # check this is defined as array
                if field_info.get("$ref") is not None:
                    if str(link.cardinality) != "One":
                        return ValidatedErrorValue(
                            module=module,
                            type=typ,
                            property=field_name,
                            error_message=f"{field_name}'s cardinality in EdgeDB is not One, but defined as One",
                        )

                elif (
                    field_info.get("type") == "array"
                    and field_info.get("items", dict()).get("$ref") is not None
                ) and str(link.cardinality) != "Many":
                    return ValidatedErrorValue(
                        module=module,
                        type=typ,
                        property=field_name,
                        error_message=f"{field_name}'s cardinality in EdgeDB is not Many, but defined as Array",
                    )

        return None

    def _check_is_valid_property(
        self,
        module: str,
        typ: str,
        properties: e.Set,
        field: t.Tuple[str, t.Dict[str, t.Any]],
    ) -> t.Optional[ValidatedErrorValue]:
        (field_name, field_info) = field
        if field_name not in [prop.name for prop in properties]:
            return ValidatedErrorValue(
                module=module,
                type=typ,
                property=field_name,
                error_message=f"{field_name} not found in target",
            )

        # check cardinalities
        for prop in properties:
            if field_name == prop.name:
                # check this is defined as array
                if field_info.get("$ref") is not None:
                    if str(prop.cardinality) != "One":
                        return ValidatedErrorValue(
                            module=module,
                            type=typ,
                            property=field_name,
                            error_message=f"{field_name}'s cardinality in EdgeDB is not One, but defined as One",
                        )

                elif (
                    field_info.get("type") == "array"
                    and field_info.get("items", dict()).get("$ref") is not None
                ) and str(prop.cardinality) != "Many":
                    return ValidatedErrorValue(
                        module=module,
                        type=typ,
                        property=field_name,
                        error_message=f"{field_name}'s cardinality in EdgeDB is not Many, but defined as Array",
                    )

        return None

    async def _inspect_and_validate_model(
        self,
        client: e.AsyncIOClient,
        model: t.Type[EdgeModel],
    ) -> t.List[ValidatedErrorValue]:
        schema = model.schema()

        name = model.__name__ if model.Config.name is None else model.Config.name
        module = model.Config.module

        type_name = f"{module}::{name}"

        # TODO(Hazealign): Migrate to Query Builder when Query Builder implemented
        result: e.Object = await client.query_single(
            """
                with module schema select ObjectType {
                    name,
                    abstract,
                    bases: { name },
                    links: {
                        name,
                        cardinality,
                        required,
                        target: { name },
                    },
                    properties: {
                        name,
                        cardinality,
                        required,
                        target: { name },
                    },
                    constraints: { name },
                } filter .name = '{type_name}' limit 1;
            """.replace(
                "{type_name}", type_name
            )
        )

        if result is None:
            return [
                ValidatedErrorValue(
                    module=module,
                    type=name,
                    error_message=f"{type_name} can't inspected in EdgeDB",
                )
            ]

        errors: t.List[ValidatedErrorValue] = []

        if result.abstract:
            errors.append(
                ValidatedErrorValue(
                    module=module,
                    type=name,
                    error_message=f"{type_name} is abstract type. It can't be validated.",
                )
            )

        # check errors in outline
        error_outlines = self._check_outline_properties(module, name, result, schema)
        if len(error_outlines) > 0:
            return error_outlines

        for (field_name, field_info) in schema["properties"].items():
            # Process as Link
            if field_info.get("$ref") is not None or (
                field_info.get("type") == "array"
                and field_info.get("items").get("$ref") is not None
            ):
                property_error = self._check_is_valid_link(
                    module, name, result.links, (field_name, field_info)
                )
            # Process as Property
            else:
                property_error = self._check_is_valid_property(
                    module, name, result.properties, (field_name, field_info)
                )

            if property_error is not None:
                errors.append(property_error)

        return errors

    async def validate(self) -> bool:
        """
        Validate all models in the database.
        We don't use ReflectedModels in this Validation. And uses pydantics schema for Validation.
        This brings to some advantage for checking referenced types.

        :return: bool - True if all models are valid, otherwise raises ValidationError
        :raise: ValidationError - if any model is invalid
        """
        # check models first
        subclass_errors: t.List[ValidatedErrorValue] = []
        for model in self._models:
            if not issubclass(model, EdgeModel):
                subclass_errors.append(
                    ValidatedErrorValue(
                        error_message=f"{model.__name__} is not a subclass of EdgeModel",
                    )
                )

        if len(subclass_errors) > 0:
            raise ValidationError(
                subclass_errors, "Validation Failure in Model's inheritance."
            )

        # inspect and validate outlines
        # it can check not included types in self._models
        outline_errors = await self._inspect_and_validate_outlines(client=self._client)
        if len(outline_errors) > 0:
            raise ValidationError(
                outline_errors,
                "Validation Failure in Outline Inspection with EdgeDB.",
            )

        # use asyncio.gather to run all inspections-validations in parallel.
        # inspect and validate each models
        unflatten_errors: t.List[t.List[ValidatedErrorValue]] = list(
            await asyncio.gather(
                *[
                    self._inspect_and_validate_model(client=self._client, model=model)
                    for model in self._models
                ]
            )
        )

        # flatten errors from each model validation errors
        errors = [item for sublist in unflatten_errors for item in sublist]

        # if errors exists throw it
        if len(errors) > 0:
            raise ValidationError(errors, "Validation Failure with EdgeDB Inspection.")

        # validation success
        return True

    async def aclose(self):
        """
        Close the EdgeDB AsyncIOClient
        """
        await self._client.aclose()
