from enum import Enum


class Sex(str, Enum):
    MALE = "Male"
    FEMALE = "Female"


class MaritalStatus(str, Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"
    SEPARATED = "Separated"


class BloodGroup(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    UNKNOWN = "Unknown"


class Genotype(str, Enum):
    AA = "AA"
    AS = "AS"
    AC = "AC"
    SS = "SS"
    SC = "SC"
    CC = "CC"
    UNKNOWN = "Unknown"


class Relationship(str, Enum):
    SPOUSE = "Spouse"
    FATHER = "Father"
    MOTHER = "Mother"
    SON = "Son"
    DAUGHTER = "Daughter"
    BROTHER = "Brother"
    SISTER = "Sister"
    UNCLE = "Uncle"
    AUNT = "Aunt"
    GRANDPARENT = "Grandparent"
    GRANDCHILD = "Grandchild"
    FRIEND = "Friend"
    EMPLOYER = "Employer"
    GUARDIAN = "Guardian"
    OTHER = "Other"