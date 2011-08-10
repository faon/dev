#!/usr/bin/perl
# feh : imgage viewer

use CGI;
use Fcntl;
$query = new CGI;
my $PICT;
my $BASE;
my @LS;
my $sel,$where,$what,$quality,$dist,$todo;

my @QUALITY=('KO','keep','OK','GOOD','NICE','BEST');
my @DIST=("cm","dm","m","Dm","Hm","km");
my @WHERE=("animal","plant","milieu","landscape","people","family sl","misc");
my @WHAT=("home","garden","city","country","work","trip","misc");


my $STY0="STYLE='color: #FFFFFF; font-family: Verdana; font-weight: bold; font-size: 24px; background-color: green;' ";
my $STY1="STYLE='color: #FFFFFF; font-family: Verdana; font-weight: bold; font-size: 20px; background-color: green;' ";

# ----------------------------------------------------------------
sub readRec  {                        # ( recfile imgfile -- val )
   my ($recfile,$imgfile)=@_;
   my $value='-';
   my ($b,$img)=splitName($imgfile);  # safe
   my $rec=`grep $img $cwd/$recfile | tail -1 `; chomp $rec;
   if ( $rec ne '' ) {
     (my $x,$value)=split(/:/,$rec);
   }
   # print "== REC:$rec VAL:$value ==\;"; 
   return($value);
}

# ---------------------------------------------------------------e
sub writeRec {                      # ( recfile imgfile val -- )
  my ($recfile, $imgfile, $val)=@_;
  my $rec=readRec($recfile, $imgfile);  # already a value ?
  if ( $rec eq '-' ) {  # not found
    system(" echo '$imgfile:$val' >> $recfile");
  }
  else  {
    system("mv $recfile /tmp; \
       sed '/^$imgfile/ s/^.*$/$imgfile:$val/' < /tmp/$recfile > $recfile");
  }
}

# ----------------------------------------------------------------
sub printChoice  {   #  ( name kind imgfile choiceList  -- )
  my ($name,$kind,$imgfile,@choiceList)=@_;
  my $v,$ck;
  my $obs=readRec("$name.rec",$imgfile);
  # print "<B>-- $name.rec $imgfile $obs -- </B>\n";
  for (my $i=0; $i<@choiceList; $i++ ) {
    $v=$choiceList[$i];
    if ( $v eq $obs )  {
       $ck='checked';
    }
    else  {
       $ck='';
    }
    print "<input type='$kind' name='$name' value='$v' $ck >$v\n"; 
  }
}

# ----------------------------------------------------------------



# ----------------------------------------------------------------
sub splitName  {
#  ( pathname -- dir basename
  my ($pathname)=@_;
  my @e=split(/\//,$pathname);
  my $basename=pop(@e);
  return(join("/",@e),$basename);
}

# ----------------------------------------------------------------
sub getPictBase  {
  my $l=`grep -i alias /etc/apache2/sites-available/default | grep '/pict/' `;
  chomp($l);
  my @t=split(" ",$l);
  $PICT=$t[2];
  $PICT=~ s/"//g;
  if ( $PICT eq '' ) {
    die("<E> no Alias /pict/ defined within apache2/sites-available/default\n");
  }
  # print "Pict=$PICT\n";
}

# ----------------------------------------------------------------
sub initParams  {
  $sel=$query->param('sel');
  $todo=$query->param('todo');
  $cwd=$query->param('cwd');
  $where=$query->param('where');
  $what=$query->param('what');
  $dist=$query->param('dist');
  $quality=$query->param('quality');

  if ( $todo eq '' && $sel eq '') {
    print "New TODO ";
    $BASE=$PICT;
    $cwd=$PICT;
    $sel=$PICT;
    $todo='CD';
  }
  elsif ($todo eq 'CD')  {
    $cwd=$sel;
  }
}

# ----------------------------------------------------------------
sub readDir  {
#   ( 
  my ($pattern)=@_;
  my @ls;
    open(IN,"ls $pattern |");
  while (<IN>) {
    chomp;
    push(@ls,$_);
  }
  return(@ls);
}

# ----------------------------------------------------------------
sub getLast  {
 my @list=readDir("$cwd/*jpg");
 print "<BR>LAST= $list[@list-1]\n";
}

sub editLast {
  getLast();
}
# ----------------------------------------------------------------
sub getFirst  {
 my @list=readDir("$cwd/*jpg");
 print "<BR>LAST= $list[0]\n";
}

sub editFirst {
  getFirst();
  editImg();
}

# ----------------------------------------------------------------
sub getNext  {
 my @list=readDir("$cwd/*jpg");
 my $idx=0;
 for (my $i=0; $i<@list-1; $i++) {
   if ( $list[$i] eq $sel ) {
      $idx=$i;
      last;
    }
  }
  $idx++;
  if ( $idx > $#list ) {
    $idx=-1
  }
  # print "<BR>NEXT= $list[$idx]\n";
  return($idx, $list[$idx]);
}

sub editNext {
  my ($idx,$file)=getNext();
  if ( $idx != -1 ) {
    $sel=$file;
    editImg();
  }
}
# ----------------------------------------------------------------
sub displayParams  {
  print "<BR>Todo=$todo\n";
  print "<BR>Sel=$sel\n";
  print "<HR>cwd=$cwd\n";
  print "<BR>Base=$BASE\n";
  print "<BR>Pict=$PICT\n";
  print "<BR>qual=$quality dist=$dist where=$where what=$what<BR>\n";
}

# ----------------------------------------------------------------
sub overview  {
   my ($current)=@_;
   my @near;
   my @list=readDir("$cwd/*jpg");
   map ( s/$PICT/\/pict/, @list );
   my $idx;

   for (my $i=0; $i<@list; $i++ ) {
     # print "IDX $idx : $list[$i] $current <BR>\n";
     if ( $list[$i] =~ /$current/ ) {
       $idx=$i;
       last;
     }
   }
   print "<TABLE><TR>\n";
   for (my $j=$idx-4; $j<$idx+5; $j++)  {
     if ( $j < 0 || $j > $#list )  {
       print "<TD bgcolor='lightgrey'> # --------------------------- # </TD>";
     }
     else  {
       my $img=$list[$j];
       my $thumb=thumbURL($img);
       my $bg='',$filler='',$width=' width="150" ';
       if ( $j == $idx ) {
          $bg=' bgcolor="green" ';
          $filler='.';
          $width='';
       }
       print "<TD$bg>$filler<A HREF='/cgi-bin/img-tag.cgi?todo=EDIT&sel=$img&cwd=$cwd'><IMG src='$thumb' $width</IMG></A>$filler</TD>\n";
     }
   }
   print "</TR></TABLE>\n";
   return("$idx/$#list");
}


# ----------------------------------------------------------------
sub browseDir {
  if ( $cwd eq '' ) {
    $cwd=$PICT;
  }
  @LS=readDir("$cwd");
  my @browsable=grep(/jpg$|^[0-9]/,@LS);
  my @jpg=grep(/jpg$/,@LS);
  print "JPG=$#jpg";
  print "<FORM  ACTION='/cgi-bin/img-tag.cgi' METHOD='post'>\n";
  print "<INPUT TYPE='SUBMIT' NAME='todo' VALUE='CD'>\n";
  if ( $#jpg > 0 ) {
    print "<INPUT TYPE='SUBMIT' NAME='todo' VALUE='init'>\n";
    print "<INPUT TYPE='SUBMIT' NAME='todo' VALUE='MOSAIC'>\n";
    print "<INPUT TYPE='SUBMIT' NAME='todo' VALUE='EDIT' $STY1>\n";
    print "<INPUT TYPE='SUBMIT' NAME='todo' VALUE='verify'>\n";
  }
  print "<OL>\n";
  for ( my $i=0; $i<@browsable; $i++ ) {
     if ( $browsable[$i] =~ "MOS-thumb.jpg" )  {
        next;
     }
     print "<LI> <input type='radio' name='sel' value='$cwd/$browsable[$i]' > $browsable[$i]\n";
  }
  print "</OL>\n";
  print "<INPUT TYPE='hidden' NAME='cwd' VALUE='$sel'></FORM>\n";
}


# ----------------------------------------------------------
sub editImg  {
  # if EDIT clicked without any selection
  if ( $sel eq '' )  {
     @LS=readDir("$cwd/*jpg");
     $sel=$LS[0];
  }
  $pict=$sel;
  $pict=~s/$PICT/\/pict/;

  my $count=overview($pict);

  print "<FORM  ACTION='/cgi-bin/img-tag.cgi' METHOD='post'>\n";
  print "<TABLE><TR><TD bgcolor='yellow'>";
  


  print "<INPUT TYPE='SUBMIT' NAME='todo' VALUE='CD' bgcolor='orange'>\n";
  print "<INPUT TYPE='SUBMIT' NAME='todo' VALUE='First'>\n";
  print "<INPUT TYPE='SUBMIT' NAME='todo' VALUE='back'>\n";
  print "<INPUT TYPE='SUBMIT' NAME='todo' VALUE='next'>\n";
  print "<INPUT TYPE='SUBMIT' NAME='todo' VALUE='Last'>\n";

    print "</TD><TD bgcolor='tan'>\n";
    printChoice("quality",'radio',$sel,@QUALITY);

    print "</TD><TD bgcolor='lightgrey'>\n";
    
    printChoice("dist",'radio',$sel,@DIST);
    #print "<input type='radio' name='dist' value='cm'>cm\n";
    print " $count \n";

    print "</TD></TR><TR><TD colspan=3>WHAT \n";
    printChoice("what",'radio',$sel,@WHAT);
    # print "<input type='radio' name='what' value='animal'>animal\n";

    print "</TD></TR><TD colspan=3>WHERE \n";
    printChoice("where",'checkbox',$sel,@WHERE);
    # print "<input type='checkbox' name='where' value='home'>home\n";
    print "<INPUT TYPE='hidden' NAME='cwd' VALUE=$cwd>\n";
    print "<INPUT TYPE='hidden' NAME='sel' VALUE=$sel>\n";
    print "</FORM></TABLE>  <IMG  SRC='$pict'>\n";
}


# -----------------------------------------------------------
sub mosaic  {
    print "<H3>Mosaic from $cwd</H3>\n";
    open(IN,"ls $cwd/MOS*jpg |");
    while (<IN>) {
      chomp;
      push(@LS,$_);
    }
    print "<OL>\n";
    for (my $i=0; $i<@LS; $i++ ) {
      my $img = $LS[$i];
      $img =~ s/$PICT/\/pict/;
      print "<LI><IMG SRC='$img'</IMG>$img LS:$LS[$i]</LI>\n";
    }
    print "</OL>\n";

}

# ------------------------------------------------------------
sub addParam  {
  my ($file,$sel,$val)=@_;
  my $cmd="echo '$sel:$val' >> $cwd/$file";
  # print "<BR> $cmd \n";
  my $output=`$cmd`; chomp($output);
  # print "<BR>OUT: $output\n";
}

# ------------------------------------------------------------
sub saveOK  {
  my ($dir,$file)=splitName($sel);
  addParam("quality.rec",$file,$quality);
  addParam("where.rec",$file,$where);
  addParam("what.rec",$file,$what);
  addParam("dist.rec",$file,$dist);  
}

# ----------------------------------------------------------
sub default  {
  print "<H2>Work on $cwd location</H2>\n";
  $MOS=`ls $cwd/MOS*jpg | wc -l`; chomp($MOS);
  $THUMB=`ls $cwd/thumbs-320 | wc -l`; chomp($THUMB);


  if ( $THUMB == 0 || $MOS == 0  ) {
     print "<H3>ERROR, no mosaics and thumbs at $cwd</H3>";
     return;
     # system("cd $cwd; /home/bin/img2mos *jpg 1> /dev/null"); 
  }
  open(IN,"ls $cwd/thumbs-320/*jpg |");
  while (<IN>) {
    chomp;
    push(@LS,$_);
  }
  print "<OL>\n";
  for (my $i=0; $i<@LS; $i++ ) {
    my $img = $LS[$i];
    $img =~ s/$PICT/\/pict/;
    print "<LI><IMG SRC='$img'</IMG>$img LS:$LS[$i]</LI>\n";
  }
  print "</OL>\n";
}

# ----------------------------------------------------------
sub showList  {
  my ($ref)=@_;
  @LS=();
  my $err=open(IN,$ref);
  while (<IN>)  {
    chomp;
    push(@LS,$_);
  }
  print "<H1> LIST $ref ($err)</H1>\n";
  for (my $i=0; $i<$#LS; $i++ ) {
    print "<IMG> SRC='$cwd/$LS[$i]</IMG>\n";
    print "<BR>$i/$#LS : $LS[$i]\n";
  }
} 

# ----------------------------------------------------------
sub full2Url  {  #  ( fulpath -- URL )
  my ( $full )= @_;
  $full=~s/$PICT/\/pict/;
  return($full);
}

# ----------------------------------------------------------
sub splitName  {   # ( fullpath -- dirname filename)
  my ($fullpath)=@_;
  my @e=split(/\//,$fullpath);
  my $basename=pop(@e);
  my $dirname=join("/",@e);
  return($dirname,$basename); 
}

# ----------------------------------------------------------
sub thumbURL  {   # ( fullpath -- thumbUrl )
  my ($img)=@_;
  my $thumb;
  if ( $img =~ /MOS/ ) {   # Mosaics do not have thumbs...
    $thumb="/pict/MOS-thumb.jpg"; # a template failover
  }
  else  {
    $img=~s/$PICT/\/pict/;  # safe, even if a URL is given
    my ($dirname,$basename)=splitName($img);
    my $radix=substr($basename,0,length($basename)-4);
    $thumb="$dirname/thumbs-266/$radix:266.jpg";
  }
  return($thumb);
}

# ----------------------------------------------------------
sub selectGroup  { 
  my ($qual)=@_;
  print "<H2> Group $qual</H2>\n";
  for (my $i=0; $i<$#LS; $i++ ) {
    my ($file,$quality)=split(/:/,$LS[$i]);
    if ( $qual  eq $quality )  {
      my $thumb=thumbURL("$cwd/$file");
      $file="$cwd/$file";
      $file=~s/$PICT/\/pict/;
      print "<A HREF='/cgi-bin/img-tag.cgi?sel=$file&todo=EDIT&cwd=$cwd' ><IMG SRC='$thumb'></A>\n";
    }
  }
}

# ----------------------------------------------------------
sub displayList  {
  my ($ref)=@_;
  @LS=();
  my $err=open(IN,$ref);
  while (<IN>)  {
    chomp;
    push(@LS,$_);
  }
  print "<H1> LIST $ref </H1>\n";
  selectGroup("nice");
  selectGroup("good");
  selectGroup("ok");
  selectGroup("keep");
  selectGroup("ko");

} 

# ----------------------------------------------------------
sub verifyDir  {
   displayList("$cwd/quality.rec");
   showList("$cwd/dist.rec");
   showList("$cwd/what.rec");
   showList("$cwd/where.rec");
}
 
# ----------------------------------------------------------
#    MAIN
# ----------------------------------------------------------

getPictBase();
print "Content-type: text/html\n\n";
print "<HTML><HEAD>";
print "<TITLE>ESSAI</TITLE></HEAD><BODY>\n";

initParams();



if ( $todo eq 'CD' )  {
  browseDir();
}
elsif ( $todo eq 'EDIT' ) {
  editImg();
}
elsif ( $todo eq 'MOSAIC' ) {
  mosaic();
}
elsif ( $todo eq 'OK' ) {
  saveOK();
  editNext();
}
elsif ( $todo eq 'Last' ) {
  editLast();
}
elsif ( $todo eq 'First' ) {
  editFirst();
}
elsif ( $todo eq 'next' ) {
  editNext();
}
elsif ( $todo eq 'verify' ) {
  verifyDir();
}
else  {
  print "<H1> ERROR : todo = $todo, not recognized</H1>\n";
  default();
}

displayParams();
print "</BODY></HTML>\n";

