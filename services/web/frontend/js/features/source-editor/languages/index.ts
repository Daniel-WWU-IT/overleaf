import { LanguageDescription } from '@codemirror/language'

export const languages = [
  LanguageDescription.of({
    name: 'latex',
    extensions: [
      'tex',
      'bib',
      'sty',
      'cls',
      'clo',
      'bst',
      'bbl',
      'pdf_tex',
      'pdf_t',
      'map',
      'fd',
      'enc',
      'def',
      'mf',
      'pgf',
      'tikz',
      'bbx',
      'cbx',
      'dbx',
      'lbx',
      'lco',
      'ldf',
      'xmpdata',
      'Rnw',
      'lyx',
      'inc',
      'dtx',
      'hak',
      'eps_tex',
      'brf',
      'ins',
      'hva',
      'Rtex',
      'rtex',
      'pstex',
      'pstex_t',
      'gin',
      'fontspec',
      'pygstyle',
      'pygtex',
      'ps_tex',
    ],
    load: () => {
      return import('./latex').then(m => m.latex())
    },
  }),
  LanguageDescription.of({
    name: 'markdown',
    extensions: ['md', 'markdown'],
    // @ts-ignore TODO: find out how to add support extensions
    load: () => {
      return import('./markdown').then(m => m.markdown())
    },
  }),
]
