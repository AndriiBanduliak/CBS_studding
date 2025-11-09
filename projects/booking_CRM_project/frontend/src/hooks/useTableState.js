import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

export function useTableState(defaults = { page: 1, pageSize: 10 }) {
  const [params, setParams] = useSearchParams()
  const [state, setState] = useState({
    page: Number(params.get('page')) || defaults.page,
    pageSize: Number(params.get('pageSize')) || defaults.pageSize,
    sort: params.get('sort') || undefined,
    order: params.get('order') || undefined,
  })

  useEffect(() => {
    const next = new URLSearchParams(params)
    next.set('page', state.page)
    next.set('pageSize', state.pageSize)
    if (state.sort) next.set('sort', state.sort); else next.delete('sort')
    if (state.order) next.set('order', state.order); else next.delete('order')
    setParams(next, { replace: true })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.page, state.pageSize, state.sort, state.order])

  const tableProps = useMemo(() => ({
    pagination: {
      current: state.page,
      pageSize: state.pageSize,
      onChange: (p, ps) => setState(s => ({ ...s, page: p, pageSize: ps })),
    },
    onChange: (_, __, sorter) => {
      const field = Array.isArray(sorter) ? sorter[0]?.field : sorter?.field
      const order = Array.isArray(sorter) ? sorter[0]?.order : sorter?.order
      setState(s => ({ ...s, sort: field, order }))
    },
  }), [state.page, state.pageSize])

  return { state, setState, tableProps }
}


