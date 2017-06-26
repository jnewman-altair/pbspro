#!/usr/bin/perl
use strict;
use warnings;
my $device;
my $input='/proc/net/dev';
my @headers;
print "\"net\":\n";
open my $DEV ,q/</,$input or die "Unable to open $input:$!\n";
while ( my $line =<$DEV> ){
	chomp $line;
	if ( not defined $headers[0] and $line =~ m/\|(bytes.*)\|/xms){
		@headers=split q/\s+/,$1;
		next;
	}
	elsif ( not defined $headers[0] ){ next; }
	elsif ( $line =~ m/^\s*(\S+):\s+(.*)/xms ){
		my $dev=$1;
		my @values=split q/\s+/,$2;
		print "{ \"dev\":\"$dev\" \"type\":{\n";
		my $vid=0;
		foreach my $type (qw/Receive Transmit/ ){
			print "\t\"$type\":{\n";
			my $id=0;
			while ( defined $headers[$id] ){
				my $valueid=$vid+$id;
				print "\t\t\"$headers[$id]\":$values[$valueid],\n";
				$id++;
			}
			print "\t},\n";
			$vid=scalar @headers;
		}
		print "}\n";
	}
}
close $DEV;
