grammar DXBCTable;

COMMENT_START: '//' -> skip;
WS: [ \r\t]+ -> skip;
NEWLINE: '\n';

ID: ([0-9a-zA-Z_/])+;
SEP: '-'+ -> skip;

table: NEWLINE* (table_row NEWLINE+)+;

table_row: ID+;