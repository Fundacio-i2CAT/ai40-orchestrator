#!/usr/bin/perl

use strict;

my $name = shift @ARGV || die "\nLack of commit name\n\n";

map { $name .= " $_"; } @ARGV;

my @files = ( "commit.pl",
	      "*.py",
	      "../requirements.txt",
	      "../orchestapi.py",
	      "tests.sh",
	      "tenor_mods/*.rb",
	      "samples/*.json",
	      "samples/*.md",
	      "templates/*.json",
	      "templates/*.md",
	      "README.md"
	    );

map { system("git add tenor_client/$_\n"); } @files;

system("git commit -m '$name'\n");
