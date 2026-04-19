#let fonts = (
  text: ("CMU Serif", "Libertinus Serif"),
  sans_serif: ("CMU Sans Serif",),
  math: ("New Computer Modern Math",),
  mono: ("DejaVu Sans Mono",),
)

#let colors = (
  title: color.black,
  headers: color.black,
  partfill: color.black,
  label: color.red,
  hyperlink: color.blue,
  strong: rgb("#000055"),
)

#let toc = {
  show outline.entry: it => {
    link(
      it.element.location(),
      it.indented([#it.prefix() ], it.inner()),
    )
    v(0.15em)
  }

  show outline.entry.where(level: 1): it => {
    set outline.entry(fill: none)
    v(1.25em, weak: true)
    text(weight: "bold", font: fonts.text, it, size: 0.85em)
  }

  text(fill: colors.title, size: 1.25em, font: fonts.text, [*Contents*])
  
  v(0.25em)
  
  outline(
    title: none,
    indent: 1.25em,
  )
}

// Unnumbered Heading Commands
#let h1(..args) = heading(level: 1 , outlined: false, numbering: none, ..args)
#let h2(..args) = heading(level: 2 , outlined: false, numbering: none, ..args)
#let h3(..args) = heading(level: 3 , outlined: false, numbering: none, ..args)
#let h4(..args) = heading(level: 4 , outlined: false, numbering: none, ..args)
#let h5(..args) = heading(level: 5 , outlined: false, numbering: none, ..args)


// Shorthands
#let pm = sym.plus.minus
#let int = sym.integral

#let url(s) = {
  link(s, text(font: fonts.mono, s))
}

#let part(s) = {
  heading(text(fill: colors.headers, s))
}
// Show rule for appendix sections  
#let appendix(s) = {
  set heading(numbering: "A.1", supplement: [Appendix])
  counter(heading).update(0)
  s
}

// Utility
#let to-string(content) = {
  if content.has("text") {
    content.text
  } else if content.has("children") {
    content.children.map(to-string).join("")
  } else if content.has("body") {
    to-string(content.body)
  } else if content == [ ] {
    " "
  }
}

// Main entry
#let zhening(
  title: none,
  author: none,
  subtitle: none,
  date: none,
  maketitle: true,
  report-style: false,
  body
) = {
  if (title != none) {
    set document(title: title)
  }
  if (author != none) {
    set document(author: to-string(author.names))
  }
  
  // Figures formatting
  show figure.caption: cap => context {
    set text(size: 8pt, font: fonts.sans_serif)
    block(inset: (x: 5em), [
      #set align(left)
      #text(weight: "bold")[#cap.supplement #cap.counter.display(cap.numbering)]#cap.separator#cap.body
    ])
  }

  // Table formatting
  set table(
    inset: (x: 6pt, y: 6pt),
    stroke: (_, y) => {
      if y == 0 {
        (bottom: 0.5pt)  // midrule
      } 
    },
  )

  show table.cell.where(y: 0): set text(weight: "bold")
  show table: block.with(stroke: (y: 1pt)) // toprule + bottomrule
  show table: set text(size: 0.85em, font: fonts.sans_serif)

  // Figure formatting 
  set figure(
    gap: 1.5em,
  )

  // Report parameters
  

  // General settings
  set page(
    paper: "a4",
    margin: (x: 2.0cm, y: 2.07cm),
    // header: context {
    //   set align(right)
    //   set text(size: 0.8em)
    //   if (not maketitle or counter(page).get().first() > 1) {
    //     if (author != none) {
    //       text(style: "italic", author.names)         
    //     }
    //   }
    // },
    numbering: "1",
  )
  
  set text(
    font: fonts.text,
    size: 10pt,
    fallback: false,
  )

  set par(
    spacing: 0.85em,
    leading: 0.55em,
    first-line-indent: 1em,
  )


  // Indent lists
  set enum(indent: 1em, spacing: 0.75em)
  set list(indent: 1em)

  // Section headers
  set heading(numbering: "1.1")
  show heading: it => {
    set text(fill: colors.headers)
    block([
      #if (it.numbering != none) [
        #text(fill:colors.headers,
          (if (report-style and it.level == 1) { "Chapter " } else { "§" })
          + counter(heading).display()
          + (if (report-style and it.level == 1) { "." } else { "" })
        )
        #h(0.2em)
      ]
      #it.body
    ])
  }
  show heading: set text(font: fonts.text, size: 11pt)
  show heading.where(level: 1): set text(size: 14pt)
  show heading.where(level: 2): set text(size: 12pt)

  // Pretty hyperlinks
  show link: it => {
    set text(fill:
      if (type(it.dest) == label) { colors.label } else { colors.hyperlink }
    )
    it
  }
  show ref: it => {
    link(it.target, it)
  }


  // --- Title page ---
  if maketitle {
    v(2.5em)
    set align(center)
    set block(spacing: 1.5em)
    block(smallcaps(text(fill:colors.title, size:1.35em, font:fonts.text, weight: 600, title)))
    if (subtitle != none) {
      block(text(size:1.2em, font:fonts.text, weight: "medium", subtitle))
    }
    if (author != none) {
      block(text(size:1.1em, style: "italic")[#author.names \ #author.institutions])
    }
    
    if (type(date) == datetime) {
      block(text(size:1em, date.display("[day] [month repr:long] [year]")))
    }
    else if (date != none) {
      block(text(size:1em, date))
    }
    v(1.5em)
  }
  body
}