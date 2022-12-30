% NiCad function extractor, C
% Jim Cordy, January 2008

% Revised Oct 2020 - new source file name protocol - JRC
% Revised Aug 2012 - disallow ouput forms in input parse - JRC
% Revised July 2011 - ignore BOM headers in source
% Revised 30.04.08 - unmark embedded functions - JRC

% NiCad tag grammar
include "nicad.grm"

% Using Gnu C grammar
% include "fortran.grm"
include "fortranClean.grm"

% Redefinitions to collect source coordinates for function definitions as parsed input,
% and to allow for XML markup of function definitions as output

% Add to KindSelector to allow real*8 and similar statements
redefine KindSelector
%  '( 'kind= [Expr] ') 
%| '( [Expr] ') 
	...
	| '* [Expr]
end define

redefine function_definition
	% Input form 
		[repeat CommentOrNewline]
		[IN_6][ProgramUnit][EX_6]
		[repeat CommentOrNewline]
end redefine

% NiCad blind renaming - C functions
% Jim Cordy, May 2010

% Rev 19.5.20 JRC - Added blind renaming for numeric and string literals


define potential_clone
    [function_definition]
end define

% Make sure that C grammar robustness does not eat NiCad tags
% redefine unknown_declaration_or_statement
%     [not endsourcetag] ...
% end redefine

redefine xml_source_coordinate
    '<source [SPOFF] 'file=[Scon] [SP] 'startline=[Scon] [SP] 'endline=[Scon] '> [SPON] [newline]
end redefine

redefine end_xml_source_coordinate
    '</source> [newline]
end redefine

% Generic blind renaming
include "generic-rename-blind.rul"

% Literal renaming for C
include "f90-rename-literals.rul"