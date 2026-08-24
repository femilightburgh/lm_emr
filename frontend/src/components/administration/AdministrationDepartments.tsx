import {
  useEffect,
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
    setEditingDepartment(null)
    setName('')
    setCode('')
    setCategory('Clinical')
    setStatus('Active')
  }


  function beginEdit(
    department: Department,
  ) {
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


  // ==========================================================================
  // Render
  // ==========================================================================

  return (
    <div>

      {error && (
        <div className="admin-error">
          {error}
        </div>
      )}


      {/* ==================================================================== */}
      {/* Department Form                                                      */}
      {/* ==================================================================== */}

      <section className="workspace-section">

        <div className="section-heading">

          <div>
            <p className="eyebrow">
              ORGANIZATION
            </p>

            <h3>
              {editingDepartment
                ? 'Edit department'
                : 'Create department'}
            </h3>

            <p>
              Configure the departments
              available to the hospital.
            </p>
          </div>

        </div>


        <form
          onSubmit={
            handleSubmit
          }
        >

          <div className="admin-form-grid">

            <label>
              Department name

              <input
                value={name}
                onChange={event =>
                  setName(
                    event.target.value,
                  )
                }
                placeholder="e.g. Cardiology"
                disabled={saving}
              />
            </label>


            <label>
              Department code

              <input
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
            </label>


            <label>
              Category

              <select
                value={category}
                onChange={event =>
                  setCategory(
                    event.target.value as DepartmentCategory,
                  )
                }
                disabled={saving}
              >

                {categories.map(
                  item => (
                    <option
                      key={item}
                      value={item}
                    >
                      {item}
                    </option>
                  ),
                )}

              </select>

            </label>


            <label>
              Status

              <select
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

            </label>

          </div>


          <div className="admin-form-actions">

            <button
              type="submit"
              className="primary-button"
              disabled={saving}
            >
              {saving
                ? 'Saving...'
                : editingDepartment
                  ? 'Update Department'
                  : 'Create Department'}
            </button>


            {editingDepartment && (
              <button
                type="button"
                className="secondary-button"
                onClick={
                  resetForm
                }
                disabled={saving}
              >
                Cancel
              </button>
            )}

          </div>

        </form>

      </section>


      {/* ==================================================================== */}
      {/* Department List                                                      */}
      {/* ==================================================================== */}

      <section
        className="workspace-section"
        style={{
          marginTop: '1rem',
        }}
      >

        <div className="section-heading">

          <div>
            <p className="eyebrow">
              HOSPITAL STRUCTURE
            </p>

            <h3>
              Departments
            </h3>
          </div>

        </div>


        {loading && (
          <div className="admin-empty-state">
            Loading departments...
          </div>
        )}


        {!loading &&
          departments.length === 0 && (
            <div className="admin-empty-state">
              No departments have been
              configured yet.
            </div>
          )}


        {!loading &&
          departments.length > 0 && (
            <div
              style={{
                display: 'grid',
                gap: '0.75rem',
              }}
            >

              {departments.map(
                department => (
                  <div
                    key={
                      department.id
                    }
                    className="admin-staff-card"
                  >

                    <div className="admin-staff-details">

                      <div>
                        <strong>
                          {department.name}
                        </strong>

                        <p>
                          Code:{' '}
                          {department.code}
                        </p>
                      </div>


                      <div>
                        <p>
                          Category
                        </p>

                        <strong>
                          {
                            department.category
                          }
                        </strong>
                      </div>


                      <div>
                        <p>
                          Status
                        </p>

                        <strong>
                          {
                            department.status
                          }
                        </strong>
                      </div>


                      <div
                        style={{
                          display: 'flex',
                          gap: '0.5rem',
                          alignItems:
                            'center',
                        }}
                      >

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
                          className="secondary-button"
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

                  </div>
                ),
              )}

            </div>
          )}

      </section>

    </div>
  )
}