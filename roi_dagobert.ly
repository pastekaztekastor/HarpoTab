\version "2.24.0"

\header {
  title = "Le bon roi Dagobert"
  composer = "Chanson traditionnelle française"
}

melody = \relative c' {
  \clef treble
  \key c \major
  \time 2/4
  \tempo "Allegretto"

  % Le bon roi Dagobert
  c8 c d e | f4 e8 d | c4 c8 d | e4 e |
  % Avait sa culotte à l'envers
  f8 f g a | g4 f8 e | d4 e8 f | e4 d |
  % Le grand saint Éloi
  c8 c d e | f4 e8 d | c4 c8 d | e4 e |
  % Lui dit: Ô mon roi!
  f8 f g a | g4 f8 e | d4 d8 d | c4 r |
  \bar "|."
}

\score {
  \new Staff {
    \melody
  }
  \layout { }
  \midi { }
}
