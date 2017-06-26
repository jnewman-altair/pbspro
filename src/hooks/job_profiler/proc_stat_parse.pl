#!/usr/bin/perl
use strict;
use warnings;
my $src='/proc/stat';
my $cpuprinted=0;
open my $STAT , q/</, $src or die "Unable to read $src: $!\n";
while ( my $line = <$STAT> ){
	chomp $line;
	if ( $line =~ m/^cpu(\d*)\s+(.*)/xms ){
		my $id=$1;
		my $value=$2;
		my @values=split q/\s+/,$value;
		if ( ! $cpuprinted ){ print "\"cpu\":{\n"; $cpuprinted=1;}
		print "\t\t\"cpu$id\":{ ";
		print "\"user\":$values[0], ";
		print "\"nice\":$values[1], ";
		print "\"system\":$values[2], ";
		print "\"idle\":$values[3], ";
		print "\"iowait\":$values[4], ";
		print "\"irq\":$values[5], ";
		print "\"softirq\":$values[6],},\n";
	} elsif ( $line =~ m/^intr\s+(\d+)/xms ){
		print "\t}\n\"intr\":$1,\n";
	} elsif ( $line =~ m/^processes\s+(\d+)/xms ){
		print "\"processes\":$1,\n";
	} elsif ( $line =~ m/^procs_running\s+(\d+)/xms ){
		print "\"procs_running\":$1,\n";
	}
}
close $STAT;
