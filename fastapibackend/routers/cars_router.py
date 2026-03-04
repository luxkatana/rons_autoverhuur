import strawberry
from typing import Optional
import pydantic
from db import vosautos, cars as carsDB
from pydantic_mongo import ObjectIdField
from strawberry.fastapi import GraphQLRouter


@strawberry.input
class Pagination:
    items_amount: Optional[int] = 2
    current_page: int


class VosCarDatabase(pydantic.BaseModel):
    id: ObjectIdField = pydantic.Field(alias="_id")
    age: int
    brand: str
    class_: str = pydantic.Field(alias="class")
    model: str
    roofbox_option: bool
    seats: int
    towbar: bool
    type: str = pydantic.Field(alias="type")
    winter_tires: bool


#    available: bool
# TODO: Implement available flag


class DatabaseCar(pydantic.BaseModel):
    id: ObjectIdField = pydantic.Field(alias="_id")
    age: int
    brand: str
    class_: str = pydantic.Field(alias="class")
    model: str
    roofbox_option: bool
    seats: int
    towbar: bool
    type: str = pydantic.Field(alias="type")
    winter_tires: bool
    available: bool
    car_image_base64: str


async def get_cars(pagination: Optional[Pagination] = None) -> list[Car]:
    cars = []
    if pagination is None:
        async with carsDB.find() as cursor:
            async for car in cursor:
                cars.append(Car.from_pydantic(DatabaseCar.model_validate(car)))
    else:
        page = pagination.current_page
        pageSize = pagination.items_amount
        async with await carsDB.aggregate(
            [
                {
                    "$facet": {
                        "data": [
                            {"$skip": (page - 1) * pageSize},
                            {"$limit": pageSize},
                        ],
                    },
                },
            ]
        ) as cursor:
            async for car in cursor:
                for car in car["data"]:
                    cars.append(Car.from_pydantic(DatabaseCar.model_validate(car)))
    return cars


async def get_vos_cars(pagination: Optional[Pagination] = None):
    cars = []
    if pagination is None:
        async with vosautos.find() as cursor:
            async for car in cursor:
                cars.append(VosCar.from_pydantic(VosCarDatabase.model_validate(car)))
    else:
        page = pagination.current_page
        pageSize = pagination.items_amount
        async with await vosautos.aggregate(
            [
                {
                    "$facet": {
                        "data": [
                            {"$skip": (page - 1) * pageSize},
                            {"$limit": pageSize},
                        ],
                    },
                },
            ]
        ) as cursor:
            async for car in cursor:
                for car in car["data"]:
                    cars.append(
                        VosCar.from_pydantic(VosCarDatabase.model_validate(car))
                    )
    return cars


@strawberry.experimental.pydantic.type(model=VosCarDatabase)
class VosCar:
    id: strawberry.ID
    age: int
    brand: str
    class_: str = strawberry.field(name="class")
    model: str
    roofbox_option: bool
    seats: int
    towbar: bool
    type: str
    winter_tires: bool
    # available: bool
    # TODO: Available flag implement


@strawberry.experimental.pydantic.type(model=DatabaseCar)
class Car:
    id: strawberry.ID
    age: int
    brand: str
    class_: str = strawberry.field(name="class")
    model: str
    roofbox_option: bool
    seats: int
    towbar: bool
    type: str
    winter_tires: bool
    car_image_base64: str
    available: bool


@strawberry.type
class Query:
    cars: list[Car] = strawberry.field(resolver=get_cars)
    voscars: list[VosCar] = strawberry.field(resolver=get_vos_cars)


schema = strawberry.Schema(Query)
CarsRouter = GraphQLRouter(schema, "/cars-graphql", "apollo-sandbox", prefix="/cars")
