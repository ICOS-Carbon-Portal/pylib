from dataclasses import dataclass
from typing import Optional
from .metacore import UriResource, Person, Organization, Station

@dataclass(frozen=True)
class RoleDetails:
	role: UriResource
	start: Optional[str]
	end: Optional[str]
	weight: Optional[int]
	extra: Optional[str]

@dataclass(frozen=True)
class PersonRole:
	org: UriResource
	role: RoleDetails

@dataclass(frozen=True)
class PersonWithRoles(Person):
	roles: list[PersonRole]

@dataclass(frozen=True)
class Membership:
	person: Person
	role: RoleDetails

@dataclass(frozen=True)
class OrgWithStaff(Organization):
	staff: list[Membership]

@dataclass(frozen=True)
class StationWithStaff(Station):
	staff: list[Membership]
