#!/bin/bash

#SBATCH --mem=512M
#SBATCH --cpus-per-task=2
#SBATCH --time=12:00:00

set -e
set -u

gzip -c -d ${1} | sed '/^<doc / { s/last-modified/last_modified/ }' |
  sed '/^<doc / { s/_unk_/unknown/g }' |
  sed '/^<doc / { s/" \+"/"unknown"/g }' |
  sed '/^<doc / { s/\\"\|\/"/"/g }' |

  sed '/^[^<]/ { s/	|	/	_	/g}' |
  sed '/^[^<]/ { s/	|	/	_	/g}' |
  sed '/^[^<]/ { s/	|\([^	]\+\)|	/	\1	/g }' |
  sed '/^[^<]/ { s/	|\([^	]\+\)|	/	\1	/g }' |
  
  sed 's/&gt;/>/g' |
  sed 's/&lt;/</g' |
  sed 's/&quot;/"/g' |
  sed "s/&apos;/'/g" |
  sed 's/&amp;/\&/g' |

  grep -v '^<dup\|<\/dup\|^dupblank' |
  sed '/^<title>/,/^<\/title>/d' |
  sed '/^<keywords>/,/^<\/keywords>/d' |
  grep -v '^<meta ' | 

  sed '/^<doc / s/crx_\(emo\|clitindef\|gen\|short\|pper_2nd\|ttrat\|wlen\|slen\)="\([0-9]\+\.[0-9]\)[0-9]*"/corex_\1="\2"/g' |
  sed '/^<doc / s/ crx_[^"=]\+="[^"]\+"//g' |

  sed '/^<doc / s/ \(sourcedoctype\|sourcecharset\|nbc\|nbcprop\|nbd\|nbdprop\|avgbpc\|avgbpd\|date\|region\|city\)="[^"]\+"//g' |

  sed '/^<doc / s/ last_modified="[^"]*\(19\|20\)\([901][0-9]\)[^"]*"/ last_modified="\1\2"/' |
  sed '/^<doc / s/ last_modified="[^"]*1970[^"]*"/ last_modified="unknown"/' |
  sed '/^<doc / s/ last_modified="[^u12][^"]*"/ last_modified="unknown"/' |

  cut -f1,3,4,5,6,8,9,10,11,12,13,14,15,16,17,18 | gzip -c > ${2}

