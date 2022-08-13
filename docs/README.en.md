# EdgeGraph

## CAUTION

**Based on 2022-08-13: Still in Progress. Features are not developed.**

**EdgeGraph is Proof-of-Concept Level status, and in actively development. This API might be changed, and not stable to used in Production.**

## Introduction

EdgeGraph is add-on library for [EdgeDB Python Client](https://github.com/edgedb/edgedb-python) for provides useful features.

 - Validate Schema with EdgeDB Server (in Runtime)
 - Provides Query Builder for EdgeQL
 - Provides Object Deserializer, which can expect types in IDE or Type Checker

## Expected API

```python
from uuid import UUID

from edgegraph.query_builder import qb
from edgegraph.schema import EdgeModel
from edgegraph.validator import SchemaValidator, ValidationError


class Movie(EdgeModel):
    id: UUID
    title: str
    actors: list[Actor]


class Actor(EdgeModel):
    id: UUID
    name: str


class MovieSubResult(EdgeModel):
    id: UUID
    title: str
    trimmed_title: str


# EdgeGraph expect to validate schema on this way.
async def schema_validation(edgedb_dsn: str) -> bool:
    try:
        validator = SchemaValidator(
            check_validation_rules=False,
            fail_fast=True,
            edgedb_dsn=edgedb_dsn,
            models=[
                # Input Schema Here
                Movie,
                Actor,
            ],
            # ... More Options
        )

        await validator.validate()
        return True
    except ValidationError as err:
        error_points = err.json()
        # Check Invalid Errors in .json() like pydantic's ValidationError
        return False


# Query Builder Example of SELECT Query
async def fetch_movie_from_actor_name (actor_name: str) -> list[Movie]:
    # EdgeGraph don't support with clause of EdgeQL,
    # just put variables in Query Builder.
    query = Movie.select([
        Movie.fields.id,
        Movie.fields.title,
        qb.field("trimmed_title", qb.fn.std.str_trim(Movie.fields.title)),
    ])\
    .filter(qb.eq(qb.reference(Movie.fields.actors, Actor.fields.name), actor_name))\
    .build()

    # Can Check EdgeQL Query `query`'s type is str.
    logger.debug(query)

    # EdgeGraph'll provide EdgeGraphClient(...), that wraps EdgeDB's Client.
    # And It supports non-blocking async API only.
    movies = await edgegraph.query(query, return_type=list[MovieSubResult])
    return movies


# Query Builder Example of INSERT Query
async def insert_movie(title: str, year: int, actors: list[str]):
    # When Building Query, EdgeGraph'll provide to check this insert statment is valid(for required fields).
    query = Movie.insert()\
                .field(Movie.fields.fields.title, title)\
                .field(Movie.fields.fields.release_year, year)\
                .field(
                    Movie.fields.actors,
                    Actor.selects().filter(qb.in(Actors.fields.name, actors)),
                )\
                .build()

    logger.debug(query)

    await edgegraph.execute(query)
```

## Development

### Goals

 - In `main` branch, I'll set CI/CD. When CI/CD setted up, Everyone(includes me) can't push codes without Pull Requests. CI will check Test, Convention, Coverage first.
 - EdgeGraph uses Poetry, no setuptools.
 - EdgeGraph has minimal dependency libraries. And support IDE and Mypy as well.

### Implement TODO List

 - [ ] Validate Defined `EdgeModel` and `EdgeDB Schema`.
 - [ ] Initial Implementation of Query Builder
 - [ ] Implement Deserializer of EdgeQL Result
 - [ ] Improve Each Features (especially Query Builder)
