# typedb-query-builder💪

## Description

It's a simple and lightweight python library for creating TypeDB queries in an Object-Oriented manner, which abstracts string preprocessing from the user.

The main advantages of this solutions are:

- removing boilerplate repetitive code and string preprocessing with very readable API for building TypeDB queries
- easy integration with any changes of `typedb-client` API. As a matter of fact, these changes should be handled by `typedb-query-builder`, so that you don't have to worry about your code
- removing unnecessary issues related with typos that appeared during typing verbose queries

## Usage

The main compoenent of this packages is `typedb_query_builder.typedb_query_builder.TypeDBQueryBuilder`.

It provides you the following methods:

- `match_entity(entity_name: str, variable_name: str)` - used for adding and an entity in match queries.
- `match_relationship(relationship_name: str, variable_name: str))` - used for adding and a relationship in match queries.
- `insert_entity(entity_name: str, variable_name: str)` - used for adding and entity in insert queries.
- `insert_relationship(relationship_name: str, variable_name: str))` - used for adding a relationship in match queries.

`entity_name` and `relationship_name` are the actual names of the concepts in schema, while `variable_name` is just a variable that you want to assign to it - in the same way as you would assign a concept to a variable in a TypeDB query (note that within one query, one TypeDBQueryBuilder instance, the same variable name cannot be used for several concepts).

Each of these functions return an object of one of the following types: `TypeDBEntityQuery`, `TypeDBRelationshipQuery`. You can use these object to assign certain information to them, specifically:

`TypeDBEntityQuery` and `TypeDBRelationshipQuery` have methods:

- `has(attribute_name: str,
      attribute_value: str,
        attribute_type: str = 'string')` - which assign an attribute to an Entity or Relationship. The attribute type is provided by `attribute_name`, it's actual value by `attribute_value`. Optionally you can specify a type of the attribute according to it's value in a schema, so that the `TypeDBQueryBuilder` will be able to create the right query which will be in line with a given schema. If not provided `TypeDBQueryBuilder` will assume that the attribute is of type `string`.

Additionally, `TypeDBRelationshipQuery` has method for adding related objects:

- `relates(role: str,
      thing: Union[TypeDBEntityQuery, "TypeDBRelationshipQuery"])` - which allows you to add a Thing (Entity/Relathinship) to a given relation under a certain role provided by `role` argument. `thing` specifies what concept should be added to a relationship. It has to be already instantiated object of type `TypeDBEntityQuery` or `TypeDBRelationshipQuery`.

### Example

```python
from typedb_query_builder.typedb_query_builder import TypeDBQueryBuilder

tqb = TypeDBQueryBuilder()

p1 = tqb.match_entity('protein', 'p1')    # Add an entity of type 'protein' to a match statement with a variable 'p1'.
p1.has('protein_name', 'ACE')             # Assign an attribute of type 'protein_name' with value 'ACE'
p1.has('protein_id', 'Q1')

p2 = tqb.match_entity('protein', 'p2')    # Add a second entity of type 'protein' to a match statement with a variable 'p2'.
p2.has('protein_name', 'ACE2')            # Assign an attribute of type 'protein_name' with value 'ACE2'
p2.has('protein_id', 'Q2')
p2.has('external-id', 1, 'double')        # This entity has an attribute 'external-id' which is of type double.

pi1 = tqb.insert_relationship('protein_interaction', 'pi')  # Add a relationship of type 'protein_interaction' to insert query.
pi1.relates('associated_protein', p1)                       # Add related entities
pi1.relates('associated_protein', p2)
pi1.has('pi_id', 'PI1')                                     # Add an attribute to a relationship

tqb.compile_query()                                         # Compile query
query = tqb.get_query()                                     # Get query

print(query)
```

Result

`match $p1 isa protein, has protein_name "ACE", has protein_id "Q1"; $p2 isa protein, has protein_name "ACE2", has protein_id "Q2", has external-id 1; insert $pi (associated_protein: $p1, associated_protein: $p2) isa protein_interaction, has pi_id "PI1";`
