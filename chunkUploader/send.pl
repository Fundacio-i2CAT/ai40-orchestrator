#!/usr/bin/perl

use strict;

foreach my $file ( <x*> ) {
  print "$file\n";

# curl \
#   -F "userid=1" \
#   -F "filecomment=This is an image file" \
#   -F "image=@/home/user1/Desktop/test.jpg" \
#   localhost/uploader.php
  my $command = "curl -i -F  \"file=\@./$file\" http://192.168.10.70:9999/api/services/vmimage/test\n";
  print "$command\n";
  my $out = `$command`;
  print "$command\n";
}
