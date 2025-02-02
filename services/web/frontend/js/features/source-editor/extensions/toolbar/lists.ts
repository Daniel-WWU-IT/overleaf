import { EditorView } from '@codemirror/view'
import {
  ChangeSpec,
  EditorSelection,
  EditorState,
  SelectionRange,
} from '@codemirror/state'
import {
  getIndentation,
  getIndentUnit,
  IndentContext,
  indentString,
  syntaxTree,
} from '@codemirror/language'
import {
  ancestorNodeOfType,
  ancestorOfNodeWithType,
  ancestorWithType,
  descendantsOfNodeWithType,
} from '../../utils/tree-operations/ancestors'
import { getEnvironmentName } from '../../utils/tree-operations/environments'
import { ListEnvironment } from '../../lezer-latex/latex.terms.mjs'

export const ancestorListType = (state: EditorState): string | null => {
  const ancestorNode = ancestorWithType(state, ListEnvironment)
  if (!ancestorNode) {
    return null
  }
  return getEnvironmentName(ancestorNode, state)
}

const wrapRangeInList = (
  state: EditorState,
  range: SelectionRange,
  environment: string,
  prefix = ''
) => {
  const cx = new IndentContext(state)
  const columns = getIndentation(cx, range.from) ?? 0
  const unit = getIndentUnit(state)
  const indent = indentString(state, columns)
  const itemIndent = indentString(state, columns + unit)

  const fromLine = state.doc.lineAt(range.from)
  const toLine = state.doc.lineAt(range.to)

  // TODO: merge with existing list at the same level?
  const lines: string[] = [`${indent}\\begin{${environment}}`]
  for (const line of state.doc.iterLines(fromLine.number, toLine.number + 1)) {
    let content = line.trim()
    if (content.endsWith('\\item')) {
      content += ' ' // ensure a space after \item
    }

    lines.push(`${itemIndent}${prefix}${content}`)
  }
  if (lines.length === 1) {
    lines.push(`${itemIndent}${prefix}`)
  }

  const changes = [
    {
      from: fromLine.from,
      to: toLine.to,
      insert: lines.join('\n'),
    },
  ]

  // map through the prefix
  range = EditorSelection.cursor(range.to).map(state.changes(changes), 1)

  changes.push({
    from: toLine.to,
    to: toLine.to,
    insert: `\n${indent}\\end{${environment}}`,
  })

  return {
    range,
    changes,
  }
}

const wrapRangesInList =
  (environment: string) =>
  (view: EditorView): boolean => {
    view.dispatch(
      view.state.changeByRange(range =>
        wrapRangeInList(view.state, range, environment)
      )
    )
    return true
  }

const unwrapRangeFromList = (
  state: EditorState,
  range: SelectionRange,
  environment: string
) => {
  const node = syntaxTree(state).resolveInner(range.from)
  const list = ancestorOfNodeWithType(node, ListEnvironment)
  if (!list) {
    return { range }
  }

  const fromLine = state.doc.lineAt(range.from)
  const toLine = state.doc.lineAt(range.to)

  const listFromLine = state.doc.lineAt(list.from)
  const listToLine = state.doc.lineAt(list.to)

  const cx = new IndentContext(state)
  const columns = getIndentation(cx, range.from) ?? 0
  const unit = getIndentUnit(state)
  const indent = indentString(state, columns - unit) // decrease indent depth

  // TODO: only move lines that are list items

  const changes: ChangeSpec[] = []

  if (listFromLine.number === fromLine.number - 1) {
    // remove \begin if there are no items before this one
    changes.push({
      from: listFromLine.from,
      to: listFromLine.to + 1,
      insert: '',
    })
  } else {
    // finish the previous list for the previous items
    changes.push({
      from: fromLine.from,
      insert: `${indent}\\end{${environment}}\n`,
    })
  }

  const ensureSpace = (state: EditorState, from: number, to: number) => {
    return /^\s*$/.test(state.doc.sliceString(from, to))
  }

  for (
    let lineNumber = fromLine.number;
    lineNumber <= toLine.number;
    lineNumber++
  ) {
    const line = state.doc.line(lineNumber)
    const to = line.from + unit

    if (to <= line.to && ensureSpace(state, line.from, to)) {
      // remove indent
      changes.push({
        from: line.from,
        to,
        insert: '',
      })
    }
  }

  if (listToLine.number === toLine.number + 1) {
    // remove \end if there are no items after this one
    changes.push({
      from: listToLine.from,
      to: listToLine.to + 1,
      insert: '',
    })
  } else {
    // start a new list for the remaining items
    changes.push({
      from: toLine.to,
      insert: `\n${indent}\\begin{${environment}}`,
    })
  }

  // map the range through these changes
  range = range.map(state.changes(changes), -1)

  return { range, changes }
}

const unwrapRangesFromList =
  (environment: string) =>
  (view: EditorView): boolean => {
    view.dispatch(
      view.state.changeByRange(range =>
        unwrapRangeFromList(view.state, range, environment)
      )
    )
    return true
  }

const toggleListForRange = (
  view: EditorView,
  range: SelectionRange,
  environment: string
) => {
  const ancestorNode = ancestorNodeOfType(
    view.state,
    range.head,
    ListEnvironment
  )

  if (ancestorNode) {
    const beginEnvNode = ancestorNode.getChild('BeginEnv')
    const endEnvNode = ancestorNode.getChild('EndEnv')

    if (beginEnvNode && endEnvNode) {
      const beginEnvNameNode = beginEnvNode
        ?.getChild('EnvNameGroup')
        ?.getChild('ListEnvName')

      const endEnvNameNode = endEnvNode
        ?.getChild('EnvNameGroup')
        ?.getChild('ListEnvName')

      if (beginEnvNameNode && endEnvNameNode) {
        const envName = view.state
          .sliceDoc(beginEnvNameNode.from, beginEnvNameNode.to)
          .trim()

        if (envName === environment) {
          const beginLine = view.state.doc.lineAt(beginEnvNode.from)
          const endLine = view.state.doc.lineAt(endEnvNode.from)

          // whether the command is the only content on this line, apart from whitespace
          const emptyBeginLine = /^\s*\\begin\{[^}]*}\s*$/.test(beginLine.text)
          const emptyEndLine = /^\s*\\end\{[^}]*}\s*$/.test(endLine.text)

          // toggle list off
          const changeSpec: ChangeSpec[] = [
            {
              from: emptyBeginLine ? beginLine.from - 1 : beginEnvNode.from,
              to: emptyBeginLine ? beginLine.to : beginEnvNode.to,
              insert: '',
            },
            {
              from: emptyEndLine ? endLine.from : endEnvNode.from,
              to: emptyEndLine ? endLine.to + 1 : endEnvNode.to,
              insert: '',
            },
          ]

          const commandNodes = descendantsOfNodeWithType(
            ancestorNode,
            'Item'
          ).filter(
            commandNode =>
              view.state.sliceDoc(commandNode.from, commandNode.to) === '\\item'
          )

          if (commandNodes.length > 0) {
            // whether the command is the only content on this line, apart from whitespace
            const emptyLineBeforeItem = /^\s*\\item\{/.test(beginLine.text)

            const indentUnit = emptyLineBeforeItem
              ? getIndentUnit(view.state)
              : 0

            for (const commandNode of commandNodes) {
              changeSpec.push({
                from: commandNode.from - indentUnit,
                to: commandNode.to + 1,
                insert: '',
              })
            }
          }

          const changes = view.state.changes(changeSpec)

          return {
            range: range.map(changes),
            changes,
          }
        } else {
          // change list type
          const changeSpec: ChangeSpec[] = [
            {
              from: beginEnvNameNode.from,
              to: beginEnvNameNode.to,
              insert: environment,
            },
            {
              from: endEnvNameNode.from,
              to: endEnvNameNode.to,
              insert: environment,
            },
          ]

          const changes = view.state.changes(changeSpec)

          return {
            range: range.map(changes),
            changes,
          }
        }
      }
    }
  } else {
    // create a new list
    return wrapRangeInList(view.state, range, environment, '\\item ')
  }

  return { range }
}

export const toggleListForRanges =
  (environment: string) => (view: EditorView) => {
    view.dispatch(
      view.state.changeByRange(range =>
        toggleListForRange(view, range, environment)
      )
    )
  }

export const wrapInBulletList = wrapRangesInList('itemize')
export const wrapInNumberedList = wrapRangesInList('enumerate')
export const unwrapBulletList = unwrapRangesFromList('itemize')
export const unwrapNumberedList = unwrapRangesFromList('enumerate')
