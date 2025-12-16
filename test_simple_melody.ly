% Mélodie simple pour test HarpoTab
% Gamme de Do majeur jouable sur harmonica diatonic C

\version "2.24.0"

\header {
  title = "Test Simple Melody"
  subtitle = "Gamme de Do majeur"
}

melody = \relative c' {
  \clef treble
  \key c \major
  \time 4/4

  % Gamme montante
  c4 d e f | g a b c |

  % Gamme descendante
  c b a g | f e d c |

  \bar "|."
}

\score {
  \new Staff \melody
  \layout { }
  \midi { }
}
