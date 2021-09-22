from collections import defaultdict
from typing import List, Union


class TypeDBEntityQuery:
    def __init__(self, entity_name: str, variable_name: str) -> None:
        self.variable_name = variable_name
        self.attributes = defaultdict(list)
        self.entity_name = entity_name

    def has(
        self,
        attribute_name: str,
        attribute_value: str,
        attribute_type: str = 'string'
    ):
        self.attributes[attribute_name].append(
            {
                'value': attribute_value,
                'type': attribute_type
            }
        )
        return self

    def has_many(self, attributes: dict):
        self._check_attributes_dict_structure(attributes)
        self.attributes.update(attributes)
        return self

    def _check_attributes_dict_structure(self, attributes: dict):
        for attribute_name, attribute_value in attributes.items():
            if not type(attribute_name) is str or \
                    not type(attribute_value) is list:
                raise RuntimeError("Wrong attributes structure.")


class TypeDBRelationshipQuery:
    def __init__(self, relationship_name: str, variable_name: str) -> None:
        self.relationship_name = relationship_name
        self.attributes = defaultdict(list)
        self.variable_name = variable_name
        self.related_things = []

    def has(
        self,
        attribute_name: str,
        attribute_value: str,
        attribute_type: str = 'string'
    ):
        self.attributes[attribute_name].append(
            {
                'value': attribute_value,
                'type': attribute_type
            }
        )
        return self

    def has_many(self, attributes: dict):
        self._check_attributes_dict_structure(attributes)
        self.attributes.update(attributes)
        return self

    def relates(
        self,
        role: str,
        thing: Union[TypeDBEntityQuery, "TypeDBRelationshipQuery"]
    ):
        self.related_things.append((role, thing))
        return self

    def relates_many(
        self,
        role: str,
        things_list: List[Union[TypeDBEntityQuery, "TypeDBRelationshipQuery"]]
    ):
        self.related_things.extend(things_list)
        return self

    def _check_attributes_dict_structure(self, attributes: dict):
        for attribute_name, attribute_value in attributes.items():
            if not type(attribute_name) is str or \
                    not type(attribute_value) is list:
                raise RuntimeError("Wrong attributes structure.")


class TypeDBQueryBuilder:
    def __init__(self) -> None:
        self.query = ''
        self.match_entities = {}
        self.match_relationships = {}
        self.insert_entities = {}
        self.insert_relationships = {}

    def match_entity(self, entity_name: str, variable_name: str):
        self._check_variable_name_availability(variable_name)
        typedb_entity = TypeDBEntityQuery(entity_name, variable_name)
        self.match_entities[variable_name] = typedb_entity
        return typedb_entity

    def match_relationship(self, relationship_name: str, variable_name: str):
        self._check_variable_name_availability(variable_name)
        typedb_relationship = TypeDBRelationshipQuery(
            relationship_name,
            variable_name
        )
        self.match_relationships[variable_name] = typedb_relationship
        return typedb_relationship

    def insert_entity(self, entity_name: str, variable_name: str):
        self._check_variable_name_availability(variable_name)
        typedb_entity = TypeDBEntityQuery(entity_name, variable_name)
        self.insert_entities[variable_name] = typedb_entity
        return typedb_entity

    def insert_relationship(self, relationship_name: str, variable_name: str):
        self._check_variable_name_availability(variable_name)
        typedb_relationship = TypeDBRelationshipQuery(
            relationship_name,
            variable_name
        )
        self.insert_relationships[variable_name] = typedb_relationship
        return typedb_relationship

    def compile_query(self):
        match_query = ''
        insert_query = ''
        if self.match_entities or self.match_relationships:
            match_query = 'match '
            match_query += self.compile_entities_query('match')
            match_query += self.compile_relationships_query('match')
        if self.insert_entities or self.insert_relationships:
            insert_query = 'insert '
            insert_query += self.compile_entities_query('insert')
            insert_query += self.compile_relationships_query('insert')
        self.query = f'{match_query}{insert_query}'

    def compile_entities_query(self, query_type: str):
        if query_type not in ('match', 'insert'):
            raise RuntimeError(
                "Provided entity type should be either 'match' or 'insert'"
                )
        entities_dict = self.match_entities if query_type == 'match' \
            else self.insert_entities
        query = ''
        for variable_name, entity in entities_dict.items():
            query += f'${variable_name}'
            query += f' isa {entity.entity_name}'
            for attribute_name, attribute_values_dicts in \
                    entity.attributes.items():
                for attribute_value_dict in attribute_values_dicts:
                    attribute_value = attribute_value_dict['value']
                    attribute_type = attribute_value_dict.get('type')
                    if attribute_type in ('double', 'long', 'int'):
                        query += f', has {attribute_name} {attribute_value}'
                    else:
                        query += f', has {attribute_name} "{attribute_value}"'
            query += '; '
        return query

    def compile_relationships_query(self, query_type: str):
        if query_type not in ('match', 'insert'):
            raise RuntimeError(
                "Provided entity type should be either 'match' or 'insert'"
                )
        relationships_dict = self.match_relationships \
            if query_type == 'match' \
            else self.insert_relationships
        query = ''
        for variable_name, relationship in relationships_dict.items():
            query += f'${variable_name}'
            query += ' ('

            for related_role, related_entity in relationship.related_things:
                query += f'{related_role}: ${related_entity.variable_name}, '

            query = query[:-2]
            query = f'{query}) '

            query += f'isa {relationship.relationship_name}'

            for attribute_name, attribute_values_dicts in \
                    relationship.attributes.items():
                for attribute_value_dict in attribute_values_dicts:
                    attribute_value = attribute_value_dict['value']
                    attribute_type = attribute_value_dict.get('type')
                    if attribute_type in ('double', 'long', 'int'):
                        query += f', has {attribute_name} {attribute_value}'
                    else:
                        query += f', has {attribute_name} "{attribute_value}"'
            query += '; '

        return query

    def _check_variable_name_availability(self, variable_name: str):
        variables_names = []
        variables_names.extend(list(self.match_entities.keys()))
        variables_names.extend(list(self.match_relationships.keys()))
        variables_names.extend(list(self.insert_entities.keys()))
        variables_names.extend(list(self.insert_relationships.keys()))
        if variable_name in variables_names:
            raise RuntimeError(
                "There is a Thing already assigned to this vriable"
            )

    def get_query(self):
        return self.query


if __name__ == '__main__':
    tqb = TypeDBQueryBuilder()

    p1 = tqb.match_entity('protein', 'p1')
    p1.has('protein_name', 'ACE')
    p1.has('protein_id', 'Q1')

    p2 = tqb.match_entity('protein', 'p2')
    # p2.has('protein_name', 'ACE2')
    # p2.has('protein_id', 'Q2')
    # p2.has('id', 1, 'double')
    p2.has_many(
        {
            'protein_name': [{"value": 'ACE2'}],
            'protein_id': [{"value": "Q2"}],
            'id': [{"value": 1, "type": "double"}]
        }
    )

    pi1 = tqb.insert_relationship('protein_interaction', 'pi')
    pi1.relates('associated_protein', p1)
    pi1.relates('associated_protein', p2)
    pi1.has('pi_id', 'PI1')
    pi1.has('id', 1, 'double')

    tqb.compile_query()
    query = tqb.get_query()

    print(query)

    # tqb = TypeDBQueryBuilder()
    # p1 = tqb.match_entity('protein', 'p1')
    # p1.has('protein_name', 'ACE')
    # p1.has('protein_id', 'Q1')

    # p2 = tqb.match_entity('protein', 'p1')

    # gqe = TypeDBEntityQuery('entity1', 'e1')
    # print(gqe.entity_name)
    # l = []
    # l.append(gqe)
    # l[0].entity_name = 'e2'
    # print(gqe.entity_name)
