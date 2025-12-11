# Intégration LilyPond dans HarpoTab

## 🎼 Pourquoi LilyPond ?

**LilyPond** est le standard professionnel pour la notation musicale par ordinateur. C'est l'équivalent de LaTeX pour la musique.

### Avantages vs ReportLab

| Critère | LilyPond | ReportLab |
|---------|----------|-----------|
| **Notation musicale** | ✅ Parfaite, standard éditorial | ⚠️ Basique, dessinée manuellement |
| **Tablature harmonica** | ✅ Extension native | ⚠️ Faite maison |
| **Accords** | ✅ Chiffrage harmonique professionnel | ✅ Texte au-dessus |
| **Qualité** | ✅ Publication professionnelle | ⚠️ Correct pour démo |
| **Export MIDI** | ✅ Automatique | ❌ Non |
| **Installation** | ⚠️ Nécessite LilyPond | ✅ Juste Python |
| **Vitesse** | ⚠️ Compilation ~5-10s | ✅ Instantané |

**Verdict** : LilyPond pour partitions professionnelles, ReportLab pour tests rapides

---

## 📦 Installation de LilyPond

### Option 1 : Script automatique
```bash
./install_lilypond.sh
```

### Option 2 : Installation manuelle

#### Manjaro / Arch Linux
```bash
sudo pacman -S lilypond
```

#### Ubuntu / Debian
```bash
sudo apt-get update
sudo apt-get install lilypond
```

#### macOS (avec Homebrew)
```bash
brew install lilypond
```

#### Vérification
```bash
lilypond --version
# GNU LilyPond 2.24.x
```

---

## 🎵 Utilisation

### Dans HarpoTab (automatique)

Le système utilise **automatiquement** LilyPond s'il est installé :

```python
# Dans app.py, la génération PDF appelle automatiquement :
generate_tablature_pdf(
    tablature,
    output_path,
    tonality='C',
    use_lilypond=True  # Par défaut
)

# Si LilyPond installé → Partition professionnelle
# Sinon → Fallback ReportLab
```

### Forcer ReportLab (sans LilyPond)
```python
generate_tablature_pdf(
    tablature,
    output_path,
    use_lilypond=False  # Force ReportLab
)
```

---

## 📄 Code LilyPond Généré

### Structure du fichier .ly

```lilypond
\version "2.24.0"

\header {
  title = "Avant Toi"
  composer = "VITAA & SLIMANE"
}

% Configuration papier
\paper {
  #(set-paper-size "a4")
}

% MÉLODIE (clé de Sol uniquement)
melody = {
  \clef treble
  \key c \major
  \time 4/4

  e'4 e'4 e'4 e'4   % Mesure 1
  f'4 f'4 f'4 g'4   % Mesure 2
  % ...
}

% ACCORDS (chiffrage harmonique)
harmony = \chordmode {
  a:m1  % Am - Mesure 1
  f1    % F  - Mesure 2
  c1    % C  - Mesure 3
  g1    % G  - Mesure 4
  % ...
}

% TABLATURE HARMONICA (numéros + flèches)
harmonicaTab = {
  s4^\markup { \bold "2↑" }  % Trou 2 soufflé
  s4^\markup { \bold "1↓" }  % Trou 1 aspiré
  % ...
}

% ASSEMBLAGE FINAL
\score {
  <<
    \new ChordNames \harmony      % Accords au-dessus
    \new Staff {
      <<
        \melody                   % Portée musicale
        \harmonicaTab            % Tablature au-dessus des notes
      >>
    }
  >>
  \layout { }  % PDF
  \midi { }    % Export MIDI
}
```

---

## 🎯 Résultat PDF

### Ce que contient le PDF généré par LilyPond :

```
┌──────────────────────────────────────────────┐
│  AVANT TOI                                   │
│  VITAA & SLIMANE                             │
│                                              │
│  Am          F          C          G         │  ← Accords (ChordNames)
│  ┌────────────────────────────────────────┐  │
│  │  2↑ 2↑ 2↑ 2↑   ↓  ↓  ↓ 2↓             │  │  ← Tablature (au-dessus)
│  │  ♩  ♩  ♩  ♩    ♩  ♩  ♩  ♩              │  │  ← Notation musicale
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │  │  ← Portée (Staff)
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

**Éléments** :
1. **Titre et compositeur** en haut
2. **Accords** (Am, F, C, G) au-dessus de la portée
3. **Tablature harmonica** (2↑, 2↓...) au-dessus des notes
4. **Portée musicale** avec notation parfaite
5. **Fichier MIDI** généré automatiquement (même nom .mid)

---

## 🔧 Fonctionnement Technique

### 1. Génération du Code LilyPond

```python
from modules.lilypond_generator import LilyPondGenerator

generator = LilyPondGenerator(
    tonality='C',
    title='Avant Toi',
    composer='VITAA & SLIMANE'
)

ly_code = generator.generate_harmonica_tablature_code(
    tablature,
    chords=[(1,'Am'), (2,'F'), (3,'C'), (4,'G')]
)

# Résultat : Code .ly (texte)
```

### 2. Conversion Notes → LilyPond

```python
# Note Python
note = Note(name='C4', duration='quarter', ...)

# Devient en LilyPond
'c\'4'  # c = Do, ' = octave 4, 4 = noire

# Exemples :
'C4' → "c'4"     # Do octave 4, noire
'D5' → "d''4"    # Ré octave 5, noire
'F#4' → "fis'4"  # Fa# octave 4, noire
'Bb3' → "bes4"   # Sib octave 3, noire
'E4' → "e'2"     # Mi octave 4, blanche
```

### 3. Compilation PDF

```python
generator.compile_lilypond(ly_code, 'output.pdf')

# Exécute en shell :
# lilypond -o output avant_toi.ly
# Génère :
# - output.pdf
# - output.mid (MIDI)
```

---

## 🎼 Extensions Harmonica dans LilyPond

LilyPond a plusieurs approches pour harmonica :

### 1. **Markup au-dessus des notes** (notre méthode actuelle)
```lilypond
s4^\markup { \bold "2↑" }  % Note invisible + texte
```

**Avantages** :
- ✅ Simple à implémenter
- ✅ Fonctionne partout
- ✅ Personnalisable

**Inconvénients** :
- ⚠️ Pas de portée séparée pour tablature

### 2. **TabStaff (comme guitare)**
```lilypond
\new TabStaff {
  \tabFullNotation
  % Notes...
}
```

**Avantages** :
- ✅ Portée dédiée pour tablature
- ✅ Alignement parfait

**Inconvénients** :
- ⚠️ Nécessite adaptation pour harmonica
- ⚠️ Plus complexe

### 3. **Scheme personnalisé** (avancé)
```lilypond
#(define (harmonica-number grob)
  ; Code Scheme pour affichage personnalisé
)
```

**Avantages** :
- ✅ Contrôle total
- ✅ Peut créer portée 2 lignes

**Inconvénients** :
- ⚠️ Nécessite connaissance Scheme (Lisp)
- ⚠️ Complexe

---

## 📊 Comparaison Visuelle

### Avec LilyPond
```
  Am                F                C
  ┌─────────────────────────────────────┐
  │ 2↑ 2↑ 2↑ 2↑   ↓  ↓  ↓ 2↓          │
  │ ♩  ♩  ♩  ♩    ♩  ♩  ♩  ♩           │
  │━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
  │ Mi Mi Mi Mi   Fa Fa Fa Sol         │
  └─────────────────────────────────────┘
```

**Qualité** : Publication professionnelle

### Avec ReportLab
```
  M1          M2          M3
  ↑ SOUFFLÉ   ○2  ○2      ○2  ○2
  ─────────────────────────────────
  ↓ ASPIRÉ        ○1  ○1
  ─────────────────────────────────
```

**Qualité** : Démo, apprentissage

---

## 🚀 Workflow Complet

### 1. Upload Partition (Web)
```
Utilisateur upload : avant-toi.jpg (piano 2 portées)
```

### 2. Extraction (Python)
```python
music_data = extract_music_from_image('avant-toi.jpg')
# → Mélodie (clé de Sol) UNIQUEMENT
# → Accords détectés : Am, F, C, G
```

### 3. Parsing (Python)
```python
notes = parse_musical_notes(music_data)
# → 42 objets Note avec accords
```

### 4. Conversion Harmonica (Python)
```python
tablature = convert_to_harmonica(notes, 'C')
# → Trou 2↑, 1↓, etc.
```

### 5a. Génération LilyPond (si installé)
```python
ly_code = generate_harmonica_tablature_code(tablature)
compile_lilypond(ly_code, 'output.pdf')
# → PDF professionnel + MIDI
```

### 5b. Génération ReportLab (sinon)
```python
generate_tablature_pdf_reportlab(tablature, 'output.pdf')
# → PDF basique
```

---

## 📁 Fichiers du Projet

### Nouveaux Fichiers

```
HarpoTab/
├── modules/
│   └── lilypond_generator.py      ← Générateur LilyPond (NOUVEAU)
│
├── install_lilypond.sh             ← Script install (NOUVEAU)
├── test_lilypond.py                ← Test génération (NOUVEAU)
├── LILYPOND_INTEGRATION.md         ← Cette doc (NOUVEAU)
│
└── static/uploads/
    ├── avant_toi_lilypond.ly      ← Code généré (NOUVEAU)
    └── avant_toi_lilypond.pdf     ← PDF compilé (si LilyPond installé)
```

### Fichiers Modifiés

```
modules/pdf_generator.py
  - Ajout option use_lilypond=True
  - Appel lilypond_generator si disponible
  - Fallback ReportLab sinon
```

---

## 🧪 Tests

### Test 1 : Génération Code .ly
```bash
python test_lilypond.py
# Génère : static/uploads/avant_toi_lilypond.ly
```

### Test 2 : Compilation PDF (si LilyPond installé)
```bash
lilypond static/uploads/avant_toi_lilypond.ly
# Génère :
# - avant_toi_lilypond.pdf
# - avant_toi_lilypond.mid
```

### Test 3 : Via Interface Web
```bash
python app.py
# http://localhost:5000
# Upload partition → Conversion automatique avec LilyPond
```

---

## 📚 Ressources

### Documentation LilyPond
- Site officiel : https://lilypond.org
- Manuel notation : https://lilypond.org/doc/v2.24/Documentation/notation/
- Extensions tablature : https://lilypond.org/doc/v2.24/Documentation/notation/tablatures

### Exemples Harmonica
- https://lsr.di.unimi.it/ (LilyPond Snippet Repository)
- Rechercher "harmonica" ou "diatonic"

### Forum
- https://lists.gnu.org/mailman/listinfo/lilypond-user

---

## 🎯 Prochaines Améliorations

### Court Terme
- [x] Génération code LilyPond basique
- [x] Compilation PDF
- [x] Intégration dans workflow
- [ ] Améliorer mapping harmonica (toutes les notes)
- [ ] Ajouter bends (notes courbées)

### Moyen Terme
- [ ] Utiliser TabStaff pour portée dédiée
- [ ] Créer vraie portée 2 lignes (blow/draw)
- [ ] Support harmonica chromatique
- [ ] Annotations (doigtés, respirations)

### Long Terme
- [ ] Extension LilyPond personnalisée pour harmonica
- [ ] Portée harmonica native (2 lignes avec symboles)
- [ ] Bibliothèque de patterns harmonica
- [ ] Export vers autres formats (MuseScore, Finale)

---

## ✅ Résumé

**HarpoTab peut maintenant générer des partitions avec LilyPond !**

✅ **Code LilyPond** généré automatiquement
✅ **Partition professionnelle** (si LilyPond installé)
✅ **Mélodie** (clé de Sol uniquement)
✅ **Tablature harmonica** au-dessus des notes
✅ **Accords** en chiffrage harmonique
✅ **Export MIDI** automatique
✅ **Fallback ReportLab** si LilyPond absent

**Pour installer LilyPond** :
```bash
./install_lilypond.sh
```

**Pour tester** :
```bash
python test_lilypond.py
```

**Profitez de partitions de qualité publication ! 🎼**
