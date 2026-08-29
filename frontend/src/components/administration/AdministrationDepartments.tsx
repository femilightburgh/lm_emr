import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from 'react'

import {
  createDepartment,
  deleteDepartment,
  listDepartments,
  updateDepartment,
  type Department,
  type DepartmentCategory,
  type DepartmentStatus,
} from '../../api/departments'


interface Props {
  accessToken: string
  hospitalId: string
}


const categories:
  DepartmentCategory[] = [
    'Clinical',
    'Diagnostic',
    'Administrative',
    'Support',
  ]


export default function AdministrationDepartments({
  accessToken,
  hospitalId,
}: Props) {
  const [departments, setDepartments] =
    useState<Department[]>([])

  const [loading, setLoading] =
    useState(false)

  const [saving, setSaving] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)

  const [formMode, setFormMode] =
    useState<'create' | 'edit' | null>(null)

  const formPanelRef =
    useRef<HTMLElement | null>(null)

  const [editingDepartment, setEditingDepartment] =
    useState<Department | null>(null)

  const [name, setName] =
    useState('')

  const [code, setCode] =
    useState('')

  const [category, setCategory] =
    useState<DepartmentCategory>(
      'Clinical',
    )

  const [status, setStatus] =
    useState<DepartmentStatus>(
      'Active',
    )

  const [searchQuery, setSearchQuery] =
    useState('')


  // ==========================================================================
  // Load
  // ==========================================================================

  async function loadDepartments() {
    setLoading(true)
    setError(null)

    try {
      const response =
        await listDepartments(
          accessToken,
          hospitalId,
        )

      setDepartments(response)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load departments.',
      )
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    void loadDepartments()
  }, [accessToken, hospitalId])


  // ==========================================================================
  // Form
  // ==========================================================================

  function resetForm() {
    setFormMode(null)
    setEditingDepartment(null)
    setName('')
    setCode('')
    setCategory('Clinical')
    setStatus('Active')
    setError(null)
  }


  function beginEdit(
    department: Department,
  ) {
    setFormMode('edit')
    setEditingDepartment(
      department,
    )

    setName(
      department.name,
    )

    setCode(
      department.code,
    )

    setCategory(
      department.category,
    )

    setStatus(
      department.status,
    )

    setError(null)

    requestAnimationFrame(() => {
      formPanelRef.current?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      })
    })
  }


  async function handleSubmit(
    event: FormEvent,
  ) {
    event.preventDefault()

    const trimmedName =
      name.trim()

    const trimmedCode =
      code.trim()

    if (!trimmedName) {
      setError(
        'Department name is required.',
      )
      return
    }

    if (!trimmedCode) {
      setError(
        'Department code is required.',
      )
      return
    }

    setSaving(true)
    setError(null)

    try {
      if (editingDepartment) {
        const updated =
          await updateDepartment(
            accessToken,
            editingDepartment.id,
            {
              name: trimmedName,
              code: trimmedCode,
              category,
              status,
            },
          )

        setDepartments(
          current =>
            current.map(
              department =>
                department.id ===
                updated.id
                  ? updated
                  : department,
            ),
        )
      } else {
        const created =
          await createDepartment(
            accessToken,
            {
              hospital_id:
                hospitalId,
              name: trimmedName,
              code: trimmedCode,
              category,
              status,
            },
          )

        setDepartments(
          current => [
            ...current,
            created,
          ].sort(
            (a, b) =>
              a.name.localeCompare(
                b.name,
              ),
          ),
        )
      }

      resetForm()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : editingDepartment
            ? 'Unable to update department.'
            : 'Unable to create department.',
      )
    } finally {
      setSaving(false)
    }
  }


  async function handleDelete(
    department: Department,
  ) {
    const confirmed =
      window.confirm(
        `Delete the department "${department.name}"?`,
      )

    if (!confirmed) {
      return
    }

    setError(null)

    try {
      await deleteDepartment(
        accessToken,
        department.id,
      )

      setDepartments(
        current =>
          current.filter(
            item =>
              item.id !==
              department.id,
          ),
      )

      if (
        editingDepartment?.id ===
        department.id
      ) {
        resetForm()
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to delete department.',
      )
    }
  }


  const filteredDepartments =
    departments.filter(department => {
      const query =
        searchQuery.trim().toLowerCase()

      if (!query) {
        return true
      }

      return (
        department.name
          .toLowerCase()
          .includes(query) ||
        department.code
          .toLowerCase()
          .includes(query) ||
        department.category
          .toLowerCase()
          .includes(query)
      )
    })


  return (
    <div className="admin-panel">

      {/* ================================================================== */}
      {/* Header                                                             */}
      {/* ================================================================== */}

      <div className="page-header">

        <div>
          <p className="eyebrow">
            ORGANIZATION
          </p>

          <h2>
            Departments
          </h2>

          <p>
            Configure the organizational departments
            available to this hospital.
          </p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={() => {
            if (formMode === 'create') {
              resetForm()
              return
            }

            setFormMode('create')
            setEditingDepartment(null)
            setError(null)
            setName('')
            setCode('')
            setCategory('Clinical')
            setStatus('Active')
          }}
        >
          {formMode === 'create'
            ? 'Cancel'
            : 'Create Department'}
        </button>

      </div>


      {/* ================================================================== */}
      {/* Error                                                              */}
      {/* ================================================================== */}

      {error && (
        <div className="error-state">
          {error}
        </div>
      )}


      {/* ================================================================== */}
      {/* Department Form                                                    */}
      {/* ================================================================== */}

      {formMode !== null && (
        <section
          ref={formPanelRef}
          className="workspace-panel"
        >

          <div className="panel-header">

            <div>
              <p className="eyebrow">
                {formMode === 'edit'
                  ? 'EDIT DEPARTMENT'
                  : 'NEW DEPARTMENT'}
              </p>

              <h3>
                {formMode === 'edit'
                  ? 'Edit department'
                  : 'Create department'}
              </h3>

              <p>
                Define the department's identity
                and organizational classification.
              </p>
            </div>

          </div>


          <form
            className="shared-form-section"
            onSubmit={handleSubmit}
          >

            <div className="form-grid">

              <div className="form-field">
                <label htmlFor="department-name">
                  Department name
                </label>

                <input
                  id="department-name"
                  className="form-control"
                  value={name}
                  onChange={event =>
                    setName(
                      event.target.value,
                    )
                  }
                  placeholder="e.g. Cardiology"
                  disabled={saving}
                />
              </div>


              <div className="form-field">
                <label htmlFor="department-code">
                  Department code
                </label>

                <input
                  id="department-code"
                  className="form-control"
                  value={code}
                  onChange={event =>
                    setCode(
                      event.target.value
                        .toUpperCase(),
                    )
                  }
                  placeholder="e.g. CARD"
                  disabled={saving}
                />
              </div>


              <div className="form-field">
                <label htmlFor="department-category">
                  Category
                </label>

                <select
                  id="department-category"
                  className="form-control"
                  value={category}
                  onChange={event =>
                    setCategory(
                      event.target.value as DepartmentCategory,
                    )
                  }
                  disabled={saving}
                >
                  {categories.map(item => (
                    <option
                      key={item}
                      value={item}
                    >
                      {item}
                    </option>
                  ))}
                </select>
              </div>


              <div className="form-field">
                <label htmlFor="department-status">
                  Status
                </label>

                <select
                  id="department-status"
                  className="form-control"
                  value={status}
                  onChange={event =>
                    setStatus(
                      event.target.value as DepartmentStatus,
                    )
                  }
                  disabled={saving}
                >
                  <option value="Active">
                    Active
                  </option>

                  <option value="Inactive">
                    Inactive
                  </option>
                </select>
              </div>

            </div>


            <div className="form-actions">

              <button
                type="submit"
                className="primary-button"
                disabled={saving}
              >
                {saving
                  ? 'Saving...'
                  : editingDepartment
                    ? 'Save Changes'
                    : 'Create Department'}
              </button>

              {editingDepartment && (
                <button
                  type="button"
                  className="secondary-button"
                  onClick={resetForm}
                  disabled={saving}
                >
                  Cancel
                </button>
              )}

            </div>

          </form>

        </section>
      )}


      {/* ================================================================== */}
      {/* Department Directory                                               */}
      {/* ================================================================== */}

      <section className="workspace-panel">

        <div className="panel-header">

          <div>
            <p className="eyebrow">
              DEPARTMENT DIRECTORY
            </p>

            <h3>
              Hospital departments
            </h3>

            <p>
              {departments.length}{' '}
              department
              {departments.length === 1
                ? ''
                : 's'} configured for this hospital.
            </p>
          </div>

          <span className="staff-directory-count">
            {filteredDepartments.length} shown
          </span>

        </div>


        <div className="admin-staff-toolbar">

          <div className="admin-search">
            <input
              type="search"
              className="form-control"
              value={searchQuery}
              onChange={event =>
                setSearchQuery(
                  event.target.value,
                )
              }
              placeholder="Search department name, code or category..."
              aria-label="Search hospital departments"
            />
          </div>

        </div>


        {loading ? (
          <div className="empty-state">
            <strong>
              Loading departments...
            </strong>
          </div>
        ) : filteredDepartments.length === 0 ? (
          <div className="empty-state">

            <strong>
              {departments.length === 0
                ? 'No departments configured yet.'
                : 'No departments match your search.'}
            </strong>

            {departments.length > 0 && (
              <p>
                Try a different department name,
                code or category.
              </p>
            )}

          </div>
        ) : (
          <div className="data-table admin-departments-directory">

            <div className="
              data-table-header
              admin-departments-directory-header
            ">
              <div>
                Department
              </div>

              <div>
                Code
              </div>

              <div>
                Category
              </div>

              <div>
                Status
              </div>

              <div>
                Action
              </div>
            </div>


            {filteredDepartments.map(
              department => (
                <div
                  key={department.id}
                  className="
                    data-table-row
                    admin-departments-directory-row
                  "
                >

                  <div className="data-table-cell">
                    <strong>
                      {department.name}
                    </strong>

                    <span>
                      Hospital department
                    </span>
                  </div>


                  <div className="data-table-cell">
                    <strong>
                      {department.code}
                    </strong>
                  </div>


                  <div className="data-table-cell">
                    <span className="role-badge">
                      {department.category}
                    </span>
                  </div>


                  <div className="data-table-cell">

                    <span
                      className={
                        department.status === 'Active'
                          ? 'status-badge status-badge--active'
                          : 'status-badge status-badge--inactive'
                      }
                    >
                      {department.status}
                    </span>

                  </div>


                  <div className="
                    data-table-cell
                    admin-departments-directory-action
                  ">

                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() =>
                        beginEdit(
                          department,
                        )
                      }
                    >
                      Edit
                    </button>

                    <button
                      type="button"
                      className="danger-button"
                      onClick={() =>
                        void handleDelete(
                          department,
                        )
                      }
                    >
                      Delete
                    </button>

                  </div>

                </div>
              ),
            )}

          </div>
        )}

      </section>

    </div>
  )
}
