\version "2.24.0"

\header {
  title = "Test Simple"
  composer = "HarpoTab"
  subtitle = "Harmonica Diatonic en C"
  tagline = "Généré par HarpoTab - https://github.com/mathurinc/harpotab"
}

\paper {
  #(set-paper-size "a4")
}

melody = \relative c' {
  \key c \major
  \time 4/4
  \tempo 4 = 120

  c'4 d'4 e'4 f'4 g'4
}

harmonicaTabs = \lyricmode {
  "4B" "4D" "5B" "5D" "6B"
}

\score {
  \new Staff = "melody" <<
    \new Voice = "melodySinger" {
      \melody
    }
    \new Lyrics \lyricsto "melodySinger" {
      \harmonicaTabs
    }
  >>
  \layout {
    \context {
      \Lyrics
      \override LyricText.font-name = "monospace"
      \override LyricText.font-size = #-1
    }
  }
  \midi { }
}
