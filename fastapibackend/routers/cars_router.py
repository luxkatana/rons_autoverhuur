import strawberry
from strawberry.fastapi import GraphQLRouter


@strawberry.type
class Query:
    @strawberry.field
    async def cars(self) -> str:
        return "HAII MOM"


schema = strawberry.Schema(Query)
CarsRouter = GraphQLRouter(schema, "/cars-graphql", "apollo-sandbox")
