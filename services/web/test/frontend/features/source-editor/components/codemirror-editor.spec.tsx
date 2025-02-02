import CodeMirrorEditor from '../../../../../frontend/js/features/source-editor/components/codemirror-editor'
import { EditorProviders } from '../../../helpers/editor-providers'
import { FC } from 'react'
import { mockScope } from '../helpers/mock-scope'
import { metaKey } from '../helpers/meta-key'
import { docId } from '../helpers/mock-doc'
import { activeEditorLine } from '../helpers/active-editor-line'

const Container: FC = ({ children }) => (
  <div style={{ width: 785, height: 785 }}>{children}</div>
)

describe('<CodeMirrorEditor/>', { scrollBehavior: false }, function () {
  beforeEach(function () {
    window.metaAttributesCache.set('ol-preventCompileOnLoad', true)
    cy.interceptEvents()
    cy.interceptSpelling()
  })

  afterEach(function () {
    window.metaAttributesCache = new Map()
  })

  it('deletes selected text on Backspace', function () {
    const scope = mockScope()

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    // put the cursor on a blank line to type in
    cy.get('.cm-line').eq(16).click().as('line')

    cy.get('@line')
      .type('this is some text')
      .should('have.text', 'this is some text')
      .type('{shift}{leftArrow}{leftArrow}{leftArrow}{leftArrow}')
      .type('{backspace}')
      .should('have.text', 'this is some ')
  })

  it('renders client-side lint annotations in the gutter', function () {
    const scope = mockScope()
    scope.settings.syntaxValidation = true

    cy.clock()

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    cy.tick(1000)
    cy.clock().invoke('restore')

    // TODO: aria role/label for gutter markers?
    cy.get('.cm-lint-marker-error').should('have.length', 2)
    cy.get('.cm-lint-marker-warning').should('have.length', 0)
  })

  it('renders annotations in the gutter', function () {
    const scope = mockScope()

    scope.pdf.logEntryAnnotations = {
      [docId]: [
        {
          row: 20,
          type: 'error',
          text: 'Another error',
        },
        {
          row: 19,
          type: 'error',
          text: 'An error',
        },
        {
          row: 20,
          type: 'warning',
          text: 'A warning on the same line',
        },
        {
          row: 25,
          type: 'warning',
          text: 'Another warning',
        },
      ],
    }

    cy.clock()

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    cy.tick(1000)
    cy.clock().invoke('restore')

    // TODO: aria role/label for gutter markers?
    cy.get('.cm-lint-marker-error').should('have.length', 2)
    cy.get('.cm-lint-marker-warning').should('have.length', 1)
  })

  it('renders code in an editor', function () {
    const scope = mockScope()

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    cy.contains('Your introduction goes here!')
  })

  it('does not indent when entering new line off non-empty line', function () {
    const scope = mockScope()

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    // put the cursor on a blank line to type in
    cy.get('.cm-line').eq(16).click().type('foo{enter}')

    activeEditorLine().should('have.text', '')
  })

  it('indents automatically when using snippet', function () {
    const scope = mockScope()

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    // put the cursor on a blank line to type in
    cy.get('.cm-line').eq(16).click().as('line')

    cy.get('@line').type('\\begin{{}itemiz')
    cy.findAllByRole('listbox').contains('\\begin{itemize}').click()

    activeEditorLine().invoke('text').should('match', /^ {4}/)
  })

  it('keeps indentation when going to a new line', function () {
    const scope = mockScope()

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    // put the cursor on a blank line to type in
    cy.get('.cm-line').eq(16).click().as('line')

    // Single indentation
    cy.get('@line').trigger('keydown', { key: 'Tab' }).type('{enter}')

    activeEditorLine().should('have.text', '    ')

    // Double indentation
    activeEditorLine().trigger('keydown', { key: 'Tab' }).type('{enter}')

    activeEditorLine().should('have.text', '        ')
  })

  it('renders cursor highlights', function () {
    const scope = mockScope()

    scope.onlineUserCursorHighlights = {
      [docId]: [
        {
          label: 'Test User',
          cursor: { row: 10, column: 5 },
          hue: 150,
        },
        {
          label: 'Another User',
          cursor: { row: 7, column: 2 },
          hue: 50,
        },
        {
          label: 'Starter User',
          cursor: { row: 0, column: 0 },
          hue: 0,
        },
      ],
    }

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    cy.get('.ol-cm-cursorHighlight').should('have.length', 3)
  })

  it('does not allow typing to the document in read-only mode', function () {
    const scope = mockScope()
    scope.permissionsLevel = 'readOnly'

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    // Handling the thrown error on failing to type text
    cy.on('fail', error => {
      if (error.message.includes('it requires a valid typeable element')) {
        return
      }

      throw error
    })

    cy.get('.cm-line').eq(16).click().as('line')

    cy.get('@line').type('text')
    cy.get('@line').should('not.contain.text', 'text')
  })

  it('highlights matching brackets', function () {
    const scope = mockScope()

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    // put the cursor on a blank line to type in
    cy.get('.cm-line').eq(16).click()

    const pairs = ['()', '[]', '{}']

    pairs.forEach(pair => {
      activeEditorLine().type(pair).as('line')
      cy.get('@line').find('.cm-matchingBracket').should('exist')
      cy.get('@line').type('{enter}')
    })
  })

  it('folds code', function () {
    const scope = mockScope()

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    // select foldable line
    cy.get('.cm-line').eq(9).click().as('line')

    const testUnfoldedState = () => {
      cy.get('.cm-gutterElement').eq(11).should('have.text', '11')

      cy.get('.cm-gutterElement').eq(12).should('have.text', '12')
    }

    const testFoldedState = () => {
      cy.get('.cm-gutterElement').eq(11).should('have.text', '13')

      cy.get('.cm-gutterElement').eq(12).should('have.text', '14')
    }

    testUnfoldedState()

    // Fold
    cy.get('span[title="Fold line"]').eq(1).click()

    testFoldedState()

    // Unfold
    cy.get('span[title="Unfold line"]').eq(1).click()

    testUnfoldedState()
  })

  it('save file with `:w` command in vim mode', function () {
    window.metaAttributesCache.set('ol-preventCompileOnLoad', false)
    cy.interceptCompile()

    const scope = mockScope()
    scope.settings.mode = 'vim'

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    // Compile on initial load
    cy.waitForCompile()
    cy.interceptCompile()

    // put the cursor on a blank line to type in
    cy.get('.cm-line').eq(16).click().as('line')

    cy.get('.cm-vim-panel').should('have.length', 0)

    cy.get('@line').type(':')

    cy.get('.cm-vim-panel').should('have.length', 1)

    cy.get('.cm-vim-panel input').type('w').type('{enter}')

    // Compile after save
    cy.waitForCompile()
  })

  it('search and replace text', function () {
    const scope = mockScope()

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    cy.get('.cm-line')
      .eq(16)
      .click()
      .type(
        '{enter}text_to_find{enter}abcde 1{enter}abcde 2{enter}abcde 3{enter}ABCDE 4{enter}'
      )

    // select text `text_to_find`
    cy.get('.cm-line').eq(17).dblclick().as('lineToFind')

    // search panel is not displayed
    cy.findByRole('search').should('have.length', 0)

    cy.get('@lineToFind').type(`{${metaKey}+f}`)

    // search panel is displayed
    cy.findByRole('search').should('have.length', 1)

    cy.findByRole('textbox', { name: 'Find' }).as('search-input')
    cy.findByRole('textbox', { name: 'Replace' }).as('replace-input')

    cy.get('@search-input')
      // search input should be focused
      .should('be.focused')
      // search input's value should be set to the selected text
      .should('have.value', 'text_to_find')

    cy.get('@search-input').clear().type('abcde')

    cy.findByRole('button', { name: 'next' }).as('next-btn')
    cy.findByRole('button', { name: 'previous' }).as('previous-btn')

    // shows the number of matches
    cy.contains(`1 of 4`)

    for (let i = 4; i; i--) {
      // go to previous occurrence
      cy.get('@previous-btn').click()

      // shows the number of matches
      cy.contains(`${i} of 4`)
    }

    for (let i = 1; i <= 4; i++) {
      // shows the number of matches
      cy.contains(`${i} of 4`)

      // go to next occurrence
      cy.get('@next-btn').click()
    }

    // roll round to 1
    cy.contains(`1 of 4`)

    // matches case
    cy.contains('Aa').click()
    cy.get('@search-input').clear().type('ABCDE')
    cy.get('.cm-searchMatch-selected').should('contain.text', 'ABCDE')
    cy.get('@search-input').clear()
    cy.contains('Aa').click()

    // matches regex
    cy.contains('[.*]').click()
    cy.get('@search-input').type('\\\\author\\{{}\\w+\\}')
    cy.get('.cm-searchMatch-selected').should('contain.text', '\\author{You}')
    cy.contains('[.*]').click()
    cy.get('@search-input').clear()
    cy.get('.cm-searchMatch-selected').should('not.exist')

    // replace
    cy.get('@search-input').type('abcde 1')
    cy.get('@replace-input').type('test 1')
    cy.findByRole('button', { name: 'Replace', exact: true }).click()
    cy.get('.cm-line')
      .eq(18)
      .should('contain.text', 'test 1')
      .should('not.contain.text', 'abcde')

    // replace all
    cy.get('@search-input').clear().type('abcde')
    cy.get('@replace-input').clear().type('test')
    cy.findByRole('button', { name: /replace all/i }).click()
    cy.get('@search-input').clear()
    cy.get('@replace-input').clear()
    cy.should('not.contain.text', 'abcde')

    // close the search form, to clear the stored query
    cy.findByRole('button', { name: 'Close' }).click()
  })

  it('auto-closes custom brackets', function () {
    const scope = mockScope()

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    // put the cursor on a blank line to type in
    cy.get('.cm-line').eq(16).click().as('line')

    // { auto-closes
    cy.get('@line').type('{{}') // NOTE: {{} = literal {
    cy.get('@line').should('have.text', '{}')
    cy.get('@line').type('{Backspace}')
    cy.get('@line').should('have.text', '')

    // [ auto-closes
    cy.get('@line').type('[')
    cy.get('@line').should('have.text', '[]')
    cy.get('@line').type('{Backspace}')
    cy.get('@line').should('have.text', '')

    // $ auto-closes
    cy.get('@line').type('$')
    cy.get('@line').should('have.text', '$$')
    cy.get('@line').type('{rightArrow}{Backspace}{Backspace}')
    cy.get('@line').should('have.text', '')

    // $$ auto-closes
    cy.get('@line').type('$$')
    cy.get('@line').should('have.text', '$$$$')
    cy.get('@line').type('{rightArrow}{rightArrow}{Backspace}{Backspace}')
    cy.get('@line').should('have.text', '$$')
    cy.get('@line').type('{Backspace}{Backspace}')
    cy.get('@line').should('have.text', '')

    // \{ doesn't auto-close
    cy.get('@line').type('\\{{}')
    cy.get('@line').should('have.text', '\\{')
    cy.get('@line').type('{Backspace}{Backspace}')
    cy.get('@line').should('have.text', '')

    // \[ *does* auto-close
    cy.get('@line').type('\\[')
    cy.get('@line').should('have.text', '\\[\\]')
    cy.get('@line').type(
      '{rightArrow}{rightArrow}{Backspace}{Backspace}{Backspace}{Backspace}'
    )
    cy.get('@line').should('have.text', '')

    // \( *does* auto-close
    cy.get('@line').type('\\(')
    cy.get('@line').should('have.text', '\\(\\)')
    cy.get('@line').type(
      '{rightArrow}{rightArrow}{Backspace}{Backspace}{Backspace}{Backspace}'
    )
    cy.get('@line').should('have.text', '')

    // \$ doesn't auto-close
    cy.get('@line').type('\\$')
    cy.get('@line').should('have.text', '\\$')
    cy.get('@line').type('{Backspace}{Backspace}')
    cy.get('@line').should('have.text', '')

    // { doesn't auto-close in front of an alphanumeric character
    cy.get('@line').type('2{leftArrow}{{}')
    cy.get('@line').should('have.text', '{2')
    cy.get('@line').type('{rightArrow}{Backspace}{Backspace}')
    cy.get('@line').should('have.text', '')

    // [ doesn't auto-close in front of an alphanumeric character
    cy.get('@line').type('2{leftArrow}[')
    cy.get('@line').should('have.text', '[2')
    cy.get('@line').type('{rightArrow}{Backspace}{Backspace}')
    cy.get('@line').should('have.text', '')

    // $ doesn't auto-close in front of an alphanumeric character
    cy.get('@line').type('2{leftArrow}$')
    cy.get('@line').should('have.text', '$2')
    cy.get('@line').type('{rightArrow}{Backspace}{Backspace}')
    cy.get('@line').should('have.text', '')

    // $$ doesn't auto-close in front of an alphanumeric character
    cy.get('@line').type('2{leftArrow}$$')
    cy.get('@line').should('have.text', '$$2')
    cy.get('@line').type('{rightArrow}{Backspace}{Backspace}{Backspace}')
    cy.get('@line').should('have.text', '')

    // { does auto-close in front of a known character
    cy.get('@line').type(':{leftArrow}{{}')
    cy.get('@line').should('have.text', '{}:')
    cy.get('@line').type(
      '{rightArrow}{rightArrow}{Backspace}{Backspace}{Backspace}'
    )
    cy.get('@line').should('have.text', '')

    // [ does auto-close in front of a known character
    cy.get('@line').type(':{leftArrow}[')
    cy.get('@line').should('have.text', '[]:')
    cy.get('@line').type(
      '{rightArrow}{rightArrow}{Backspace}{Backspace}{Backspace}'
    )
    cy.get('@line').should('have.text', '')

    // $ does auto-close in front of a known character
    cy.get('@line').type(':{leftArrow}$')
    cy.get('@line').should('have.text', '$$:')
    cy.get('@line').type(
      '{rightArrow}{rightArrow}{Backspace}{Backspace}{Backspace}'
    )
    cy.get('@line').should('have.text', '')

    // $$ does auto-close in front of a known character
    cy.get('@line').type(':{leftArrow}$$')
    cy.get('@line').should('have.text', '$$$$:')
    cy.get('@line').type(
      '{rightArrow}{rightArrow}{rightArrow}{Backspace}{Backspace}{Backspace}{Backspace}{Backspace}'
    )
    cy.get('@line').should('have.text', '')

    // $ at the end of an inline "dollar math" node skips the closing $
    cy.get('@line').type('$2+3=5')
    cy.get('@line').should('have.text', '$2+3=5$')
    cy.get('@line').type('$')
    cy.get('@line').should('have.text', '$2+3=5$')
    cy.get('@line').type('{Backspace}'.repeat(7))
    cy.get('@line').should('have.text', '')
  })

  it('navigates in the search panel', function () {
    const scope = mockScope()

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    // Open the search panel
    cy.get('.cm-line').eq(16).click().type(`{${metaKey}+f}`)

    cy.findByRole('search').within(() => {
      cy.findByLabelText('Find').as('find-input')
      cy.findByLabelText('Replace').as('replace-input')
      cy.get('[type="checkbox"][name="caseSensitive"]').as('case-sensitive')
      cy.get('[type="checkbox"][name="regexp"]').as('regexp')
      cy.get('[type="checkbox"][name="wholeWord"]').as('whole-word')
      cy.get('label').contains('Aa').as('case-sensitive-label')
      cy.get('label').contains('[.*]').as('regexp-label')
      cy.get('label').contains('W').as('whole-word-label')
      cy.findByRole('button', { name: 'Replace' }).as('replace')
      cy.findByRole('button', { name: 'Replace All' }).as('replace-all')
      cy.findByRole('button', { name: 'next' }).as('find-next')
      cy.findByRole('button', { name: 'previous' }).as('find-previous')
      cy.findByRole('button', { name: 'Close' }).as('close')

      // Tab forwards...
      cy.get('@find-input').should('be.focused').tab()
      cy.get('@replace-input').should('be.focused').tab()
      cy.get('@case-sensitive').should('be.focused').tab()
      cy.get('@regexp').should('be.focused').tab()
      cy.get('@whole-word').should('be.focused').tab()
      cy.get('@find-next').should('be.focused').tab()
      cy.get('@find-previous').should('be.focused').tab()
      cy.get('@replace').should('be.focused').tab()
      cy.get('@replace-all').should('be.focused').tab()

      // ... then backwards
      cy.get('@close').should('be.focused').tab({ shift: true })
      cy.get('@replace-all').should('be.focused').tab({ shift: true })
      cy.get('@replace').should('be.focused').tab({ shift: true })
      cy.get('@find-previous').should('be.focused').tab({ shift: true })
      cy.get('@find-next').should('be.focused').tab({ shift: true })
      cy.get('@whole-word').should('be.focused').tab({ shift: true })
      cy.get('@regexp').should('be.focused').tab({ shift: true })
      cy.get('@case-sensitive').should('be.focused').tab({ shift: true })
      cy.get('@replace-input').should('be.focused').tab({ shift: true })
      cy.get('@find-input').should('be.focused')

      for (const option of [
        '@case-sensitive-label',
        '@regexp-label',
        '@whole-word-label',
      ]) {
        // Toggle when clicked, then focus the search input
        cy.get(option).click().should('have.class', 'checked')
        cy.get('@find-input').should('be.focused')

        // Toggle when clicked again, then focus the search input
        cy.get(option).click().should('not.have.class', 'checked')
        cy.get('@find-input').should('be.focused')
      }
    })
  })

  it('restores stored cursor and scroll position', function () {
    const scope = mockScope()

    window.localStorage.setItem(
      `doc.position.${docId}`,
      JSON.stringify({
        cursorPosition: { row: 50, column: 5 },
        firstVisibleLine: 45,
      })
    )

    cy.mount(
      <Container>
        <EditorProviders scope={scope}>
          <CodeMirrorEditor />
        </EditorProviders>
      </Container>
    )

    activeEditorLine()
      .should('have.text', 'contentLine 29')
      .should(() => {
        const selection = window.getSelection() as Selection
        expect(selection.isCollapsed).to.be.true

        const rect = selection.getRangeAt(0).getBoundingClientRect()
        expect(Math.round(rect.top)).to.be.gte(100)
        expect(Math.round(rect.left)).to.be.gte(90)
      })
  })
})
