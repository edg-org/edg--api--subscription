from typing import List, Optional

from fastapi import Depends
from api.models.AuthorModel import Author
from api.models.BookModel import Book

from api.repositories.AuthorRepository import AuthorRepository
from api.schemas.pydantic.AuthorSchema import AuthorSchema


class AuthorService:
    authorRepository: AuthorRepository

    def __init__(
        self, authorRepository: AuthorRepository = Depends()
    ) -> None:
        self.authorRepository = authorRepository

    def create(self, author_body: AuthorSchema) -> Author:
        return self.authorRepository.create(
            Author(name=author_body.name)
        )

    def delete(self, author_id: int) -> None:
        return self.authorRepository.delete(
            Author(id=author_id)
        )

    def get(self, author_id: int) -> Author:
        return self.authorRepository.get(
            Author(id=author_id)
        )

    def list(
        self,
        name: Optional[str] = None,
        pageSize: Optional[int] = 100,
        startIndex: Optional[int] = 0,
    ) -> List[Author]:
        return self.authorRepository.list(
            name, pageSize, startIndex
        )

    def update(
        self, author_id: int, author_body: AuthorSchema
    ) -> Author:
        return self.authorRepository.update(
            author_id, Author(name=author_body.name)
        )

    def get_books(self, author_id: int) -> List[Book]:
        return self.authorRepository.get(
            Author(id=author_id)
        ).books