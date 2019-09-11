grammar DXBC;

fragment COMPONENT: 'x' | 'y' | 'z' | 'w';
fragment DIGIT: '0'..'9';
fragment HEXDIGIT: DIGIT | 'a'..'f' | 'A'..'F';
fragment ALPHA: 'a'..'z' | 'A'..'Z';
fragment ALPHANUM: ALPHA | DIGIT | '_';


BRACE_OPEN: '{';
//BRACE_CLOSE: '}';
BRACE_LIST_START: BRACE_OPEN WS* NEWLINE?;
BRACE_LIST_END: '}';

ARRAY_IDX_OPEN: '[';
ARRAY_IDX_CLOSE: ']';

COMMA_SEP_NEWLINE: COMMA_SEP NEWLINE;

SHADER_TAG: 'ps_';
SHADER_VERSION: DIGIT '_' DIGIT;


DECL_NAME: 'dcl_' ID;
ID: ALPHA ALPHANUM+;
INSTRUCTION_START: DIGIT+ ':';
SINGLE_COMPONENT: '.' COMPONENT;
SWIZZLE_COMPONENT: '.' COMPONENT+;

COMMA_SEP: ' '* ',' ' '*;


HEX_IMMEDIATE_SCALAR: '0x' HEXDIGIT+;
INT_IMMEDIATE_SCALAR: DIGIT+;
FLOAT_IMMEDIATE_SCALAR: DIGIT+ '.' DIGIT+;

file: shader_name declarations instructions;

shader_name: ID NEWLINE;


declarations: (declaration NEWLINE)+;
declaration: 
	DECL_NAME brace_list_or_val 
	| DECL_NAME brace_list_or_val COMMA_SEP value (COMMA_SEP value)*
	| DECL_NAME brace_list_or_val value (COMMA_SEP value)*
	;
//decl_global_flags: ;


instructions: (instruction NEWLINE)+;
instruction: INSTRUCTION_START;

value: (vector_value | scalar_value);
scalar_value: immediate_scalar | single_vector_component | scalar_variable;
vector_value: immediate_vector | swizzled_vector_variable;

immediate_scalar: HEX_IMMEDIATE_SCALAR | FLOAT_IMMEDIATE_SCALAR | INT_IMMEDIATE_SCALAR;

single_vector_component: variable_name SINGLE_COMPONENT;

scalar_variable: variable_name;

immediate_vector: '(' scalar_value (COMMA_SEP scalar_value)+ ')';

swizzled_vector_variable: variable_name SWIZZLE_COMPONENT;

variable_name: ID array_index?;
array_index: ARRAY_IDX_OPEN value+ ARRAY_IDX_CLOSE;


brace_list_or_val: brace_list | value;
brace_list: BRACE_LIST_START brace_list_or_val ((COMMA_SEP | COMMA_SEP_NEWLINE) brace_list_or_val)+ BRACE_LIST_END;


WS: (' ' | '\t' | '\r')+ -> skip ; // skip tabs and return carriages
NEWLINE: '\n';