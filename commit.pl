#!/usr/bin/perl

use strict;

my $name = shift @ARGV || die "\nLack of commit name\n\n";

map { $name .= " $_"; } @ARGV;

my @files = (
	     "keys/dcs.json",
	     "chunkUploader/repoServer.py",
	     "chunkUploader/send.pl",
	     "chunkUploader/requirements.txt",
	     "chunkUploader/static/index.html",
	     "chunkUploader/static/*.js",
	     "aux/shtemplating.sh",
	     "config.cfg",
	     ".gitignore",
	     "orchestrator_tests.py",
	     "commit.pl",
	     "tenor_client/README.md",
	     "tenor_client/*.py",
	     "start.py",
	     "requirements.txt",
	     "tenor_client/samples/*.json",
	     "tenor_client/samples/*.md",
	     "tenor_client/templates/*.json",
	     "tenor_client/templates/*.md",
	     "README.md"
	    );

map { system("git add $_\n"); } @files;

system("git commit -m '$name'\n");
