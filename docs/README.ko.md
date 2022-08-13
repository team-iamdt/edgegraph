# EdgeGraph

## 경고

**2022-08-13 기준: 아직 구현이 완료되지 않음**

**EdgeGraph는 개념 증명 레벨의 라이브러리이며, 아직 활발하게 개발되고 있습니다. 설계된 API는 추후 달라질 수 있으며, Production 환경에서 쓰기에 적합하지 않을 수 있습니다.**

## 소개

EdgeGraph는 [EdgeDB Python Client](https://github.com/edgedb/edgedb-python) 위에 레이어를 추가한 라이브러리로 EdgeDB Python Client가 제공하지 않는 다음과 같은 기능을 제공합니다.

 - 현재 EdgeDB 서버와의 Schema Reflection 체크
 - EdgeDB를 위한 Query Builder를 제공
 - IDE 등에서 쉽게 타입 예측이 가능한 Object Deserialization 기능을 제공

## 어떤 API를 예상하는가?

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


# 이런 식으로 스키마를 밸리데이션할 수 있게 하는걸 목표로 합니다.
async def schema_validation(edgedb_dsn: str) -> bool:
    try:
        validator = SchemaValidator(
            check_validation_rules=False,
            fail_fast=True,
            edgedb_dsn=edgedb_dsn,
            models=[
                # 여기에 스키마 모델 입력
                Movie,
                Actor,
            ],
            # ... 추가 옵션들
        )

        await validator.validate()
        return True
    except ValidationError as err:
        error_points = err.json()
        # 여기서 Pydantic의 ValidationError처럼 .json()으로 에러 목록을 확인할 수 있게 해줍니다.
        return False


# 쿼리 빌더 예시 (Select 문의 예시입니다.)
async def fetch_movie_from_actor_name (actor_name: str) -> list[Movie]:
    # with 문으로 변수를 넣거나 하지 않고 Query Builder에서 직접 변수를 넣습니다.
    query = Movie.select([
        Movie.fields.id,
        Movie.fields.title,
        qb.field("trimmed_title", qb.fn.std.str_trim(Movie.fields.title)),
    ])\
    .filter(qb.eq(qb.reference(Movie.fields.actors, Actor.fields.name), actor_name))\
    .build()

    # EdgeQL Query를 확인할 수 있습니다. query 변수의 타입은 str입니다.
    logger.debug(query)

    # EdgeGraphClient(...)라는걸 만들어서 대략 EdgeDB Client를 감싸는걸 목표합니다.
    # 무조건 Async API만을 지원합니다.
    movies = await edgegraph.query(query, return_type=list[MovieSubResult])
    return movies


# 쿼리 빌더 예시 (Insert 문의 예시입니다.)
async def insert_movie(title: str, year: int, actors: list[str]):
    # Query를 빌드할 때 실제 required 필드가 충족되는지도 검증합니다.
    query = Movie.insert()\
                .field(Movie.fields.fields.title, title)\
                .field(Movie.fields.fields.release_year, year)\
                .field(
                    Movie.fields.actors,
                    Actor.selects().filter(qb.in(Actors.fields.name, actors)),
                )\
                .build()

    logger.debug(query)

    await edgegraph_query.execute(query)
```

## 개발 방식

### 목표

 - `main` 브랜치에는 **CI / CD가 셋팅된 후** (아직은 셋팅되지 않음)에는 아무도 PR 없이는 올릴 수 없도록 보호할 예정입니다.
 - git flow 전략을 쓰지 않고, 각자 `$username_$context` 혹은 `$context`으로 브랜치를 따서 개발합니다.
 - Poetry를 사용하며 setuptools를 사용하지 않습니다.
 - 최소한의 의존성으로, IDE와 Mypy 등에서 문제 없게 지원하는걸 목표로 합니다,

### 구현 순서

 - [ ] `EdgeModel`과 `EdgeDB Schema`가 일치하는지 검증하는 모듈 구현하기
 - [ ] Query Builder의 초기 구현
 - [ ] `EdgeQL`을 실행한 결과물을 Python 모델로 역직렬화 할 수 있는 모듈 구현
 - [ ] Query Builder와 각 기능들의 개선
