grammar DXBC;

COMPONENT: 'x' | 'y' | 'z' | 'w';
fragment DIGIT: '0'..'9';
fragment HEXDIGIT: DIGIT | 'a'..'f' | 'A'..'F';
fragment ALPHA: 'a'..'z' | 'A'..'Z';
fragment ALPHANUM: ALPHA | DIGIT | '_';

LINE_COMMENT: '//' ~('\n')* -> skip;

SAMPLE_INDEXABLE_TOKEN: 'sample_indexable(texture2d)(float,float,float,float)';

BRACE_OPEN: '{';
//BRACE_CLOSE: '}';
BRACE_LIST_START: BRACE_OPEN WS* NEWLINE?;
BRACE_LIST_END: '}';

PLUS_OP: '+';
SUB_OP: '-';

ARRAY_IDX_OPEN: '[';
ARRAY_IDX_CLOSE: ']';

COMMA_SEP_NEWLINE: COMMA_SEP NEWLINE;

SHADER_TAG: 'ps_' DIGIT '_' DIGIT;

COMPONENT_STR: COMPONENT+;

DECL_NAME: 'dcl_' ID;
ID: ALPHA ALPHANUM+;
DOT: '.';

COMMA_SEP: ' '* ',' ' '*;


VECTOR_OPEN: 'l'? '(';
VECTOR_CLOSE: ')';

INSTRUCTION_LINE_SEP: ':';

HEX_IMMEDIATE_SCALAR: '0x' HEXDIGIT+;
INT_IMMEDIATE_SCALAR: DIGIT+;
FLOAT_IMMEDIATE_SCALAR: DIGIT+ '.' DIGIT+;

dxbc_file: (NEWLINE | WS)* shader_name NEWLINE declarations NEWLINE instructions NEWLINE* EOF;

shader_name: SHADER_TAG;


declarations: declaration (NEWLINE declaration)*;
declaration: simple_declaration;
simple_declaration: DECL_NAME brace_list_or_val* value (COMMA_SEP value)*
| DECL_NAME brace_list;

//value_chain: ;

instructions: instruction (NEWLINE instruction)*;
instruction:
	INT_IMMEDIATE_SCALAR INSTRUCTION_LINE_SEP instruction_name
	| INT_IMMEDIATE_SCALAR INSTRUCTION_LINE_SEP instruction_name value (COMMA_SEP value)*;
	
instruction_name: ID | SAMPLE_INDEXABLE_TOKEN;

value: (PLUS_OP | SUB_OP)? (vector_value | scalar_value);
scalar_value: immediate_scalar | single_vector_component | scalar_variable;
vector_value: immediate_vector | swizzled_vector_variable;
component_value: (PLUS_OP | SUB_OP)? scalar_value;

immediate_scalar: HEX_IMMEDIATE_SCALAR | FLOAT_IMMEDIATE_SCALAR | INT_IMMEDIATE_SCALAR;

single_component: DOT COMPONENT;
swizzle_components: DOT COMPONENT_STR;

single_vector_component: variable_name single_component;

scalar_variable: variable_name;

immediate_vector: VECTOR_OPEN component_value (COMMA_SEP component_value)* VECTOR_CLOSE;

swizzled_vector_variable: variable_name swizzle_components;

variable_name: ID array_index?;
array_index: ARRAY_IDX_OPEN component_value+ ARRAY_IDX_CLOSE;


brace_list_or_val: brace_list | value;
brace_list: BRACE_LIST_START brace_list_or_val ((COMMA_SEP | COMMA_SEP_NEWLINE) brace_list_or_val)+ BRACE_LIST_END;


WS: [ \t\r]+ -> skip ; // skip tabs and return carriages
NEWLINE: '\n';