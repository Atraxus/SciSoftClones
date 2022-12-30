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

% Ignore BOM headers from Windows
include "bom.grm"

% Redefinitions to collect source coordinates for function definitions as parsed input,
% and to allow for XML markup of function definitions as output

% Add to KindSelector to allow real*8 and similar statements
redefine KindSelector
%  '( 'kind= [Expr] ') 
%| '( [Expr] ') 
	...
	| '* [Expr]
end define

% List of all 'end statements:
%	EndProgramStmt
%	EndFunctionStmt
%	EndSubroutineStmt
%	EndBlockDataStmt
%	EndModuleStmt
%	^^^^^^^^^^^^^^^^^ All of those are used in extract function
%	---> not interesting here?
%	These could be interesting here:
%		EndIfStmt
%		EndfileStmt
%		EndTypeStmt
%		EndWhereStmt
%		EndSelectStmt
%		EndDoStmt
%		EndInterfaceStmt

redefine function_definition
	% Input form 
		[repeat CommentOrNewline]
		[srclinenumber]
		[ProgramUnit]
		[srclinenumber]
		[repeat CommentOrNewline]
	|
	% Output form 
		[not token]
		[opt xml_source_coordinate]
		[ProgramUnit]
		[opt end_xml_source_coordinate]
end redefine

redefine program
	[repeat function_definition+] % Todo: parsing with this still fails despite normal program definition working
end redefine

% Main function - extract and mark up function definitions from parsed input program
function main
    replace [program]
		P [program]
		construct Functions [repeat function_definition]
			_ [^ P] 			% Extract all functions from program
			[convertFunctionDefinitions] 	% Mark up with XML
    by 
		Functions %[removeOptSemis]
end function

rule convertFunctionDefinitions
    import TXLargs [repeat stringlit]
	FileNameString [stringlit]

    % Find each function definition and match its input source coordinates
    replace [function_definition]
		LineNumber [srclinenumber]
		FunctionBody [ProgramUnit]
		EndLineNumber [srclinenumber]

    % Convert line numbers to strings for XML
    construct LineNumberString [stringlit]
	_ [quote LineNumber]
    construct EndLineNumberString [stringlit]
	_ [quote EndLineNumber]

    % Output is XML form with attributes indicating input source coordinates
    construct XmlHeader [xml_source_coordinate]
	'<source file=FileNameString startline=LineNumberString endline=EndLineNumberString>
    by
	XmlHeader
	FunctionBody % [unmarkEmbeddedFunctionDefinitions]
	'</source>
end rule