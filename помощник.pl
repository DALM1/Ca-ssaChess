#!/usr/bin/perl
use strict;
use warnings;

sub proverit_hod {
    my ($hod, $igrok) = @_;
    if ($hod =~ /^[a-h][1-8][a-h][1-8]$/) {
        return "Hod deystvitelen dlya $igrok: $hod";
    } else {
        return "Nedopustimyy hod: $hod";
    }
}

sub zapisat_hod {
    my ($hod) = @_;
    open my $fail, '>>', 'shahmatnye_hody.log' or die "Ne mogu otkryt fail zhurnala: $!";
    print $fail "$hod\n";
    close $fail;
    return "Hod zapisanyy: $hod";
}

while (<STDIN>) {
    chomp;
    my ($komanda, @argumenty) = split ' ', $_;

    if ($komanda eq "proverit_hod") {
        my ($hod, $igrok) = @argumenty;
        print proverit_hod($hod, $igrok), "\n";
    } elsif ($komanda eq "zapisat_hod") {
        my ($hod) = @argumenty;
        print zapisat_hod($hod), "\n";
    } else {
        print "Neizvestnaya komanda: $komanda\n";
    }
}
