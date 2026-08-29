import {
  useEffect,
  useState,
  type FormEvent,
} from 'react'

import {
  createLaboratoryAnalyte,
  createLaboratoryTest,
  listLaboratoryTests,
  updateLaboratoryAnalyte,
  type LaboratoryAnalyteDataType,
  type CreateLaboratoryAnalyteRequest,
  type LaboratoryTest,
  type LaboratoryTestAnalyte,
} from '../../api/laboratory'


interface Props {
  accessToken: string
}


export default function AdministrationLaboratoryCatalogue({
  accessToken,
}: Props) {
  const [tests, setTests] =
    useState<LaboratoryTest[]>([])

  const [selectedTestCode, setSelectedTestCode] =
    useState('')

  const [searchQuery, setSearchQuery] =
    useState('')

  const [editingAnalyteId, setEditingAnalyteId] =
    useState<string | null>(null)

  const [addingAnalyte, setAddingAnalyte] =
    useState(false)

  const [savingNewAnalyte, setSavingNewAnalyte] =
    useState(false)

  const [savingAnalyteId, setSavingAnalyteId] =
    useState<string | null>(null)

  const [error, setError] =
    useState<string | null>(null)

  const [success, setSuccess] =
    useState<string | null>(null)

  const [loading, setLoading] =
    useState(true)

  const [showCreateForm, setShowCreateForm] =
    useState(false)

  const [creatingTest, setCreatingTest] =
    useState(false)

  const [newTestName, setNewTestName] =
    useState('')

  const [newTestCode, setNewTestCode] =
    useState('')

  const [newTestSpecimen, setNewTestSpecimen] =
    useState('')

  const [newTestDescription, setNewTestDescription] =
    useState('')

  const [newAnalytes, setNewAnalytes] =
    useState<CreateLaboratoryAnalyteRequest[]>([])


  async function loadCatalogue() {
    setLoading(true)
    setError(null)

    try {
      const response =
        await listLaboratoryTests(
          accessToken,
        )

      setTests(response)

      setSelectedTestCode(
        current =>
          response.some(
            test =>
              test.code === current,
          )
            ? current
            : response[0]?.code ?? '',
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load laboratory catalogue.',
      )
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    void loadCatalogue()
  }, [accessToken])


  const selectedTest =
    tests.find(
      test =>
        test.code === selectedTestCode,
    ) ?? null

  const filteredTests =
    tests.filter(test => {
      const query =
        searchQuery.trim().toLowerCase()

      if (!query) {
        return true
      }

      return (
        test.code
          .toLowerCase()
          .includes(query) ||
        test.name
          .toLowerCase()
          .includes(query) ||
        (test.specimen ?? '')
          .toLowerCase()
          .includes(query)
      )
    })


  function resetCreateForm() {
    setShowCreateForm(false)
    setCreatingTest(false)
    setNewTestName('')
    setNewTestCode('')
    setNewTestSpecimen('')
    setNewTestDescription('')
    setNewAnalytes([])
    setError(null)
  }


  function addNewAnalyte() {
    setNewAnalytes(current => [
      ...current,
      {
        code: '',
        name: '',
        data_type: 'NUMERIC',
        unit: '',
        reference_low: null,
        reference_high: null,
        reference_text: null,
        options: null,
        required: false,
        display_order: current.length,
      },
    ])
  }


  function updateNewAnalyte(
    index: number,
    updates: Partial<CreateLaboratoryAnalyteRequest>,
  ) {
    setNewAnalytes(current =>
      current.map(
        (analyte, analyteIndex) =>
          analyteIndex === index
            ? {
                ...analyte,
                ...updates,
              }
            : analyte,
      ),
    )
  }


  function removeNewAnalyte(
    index: number,
  ) {
    setNewAnalytes(current =>
      current
        .filter(
          (_, analyteIndex) =>
            analyteIndex !== index,
        )
        .map(
          (analyte, analyteIndex) => ({
            ...analyte,
            display_order: analyteIndex,
          }),
        ),
    )
  }


  async function handleCreateTest(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const name =
      newTestName.trim()

    const code =
      newTestCode.trim().toUpperCase()

    const specimen =
      newTestSpecimen.trim()

    const description =
      newTestDescription.trim()

    if (!name) {
      setError(
        'Investigation name is required.',
      )
      return
    }

    if (!code) {
      setError(
        'Investigation code is required.',
      )
      return
    }

    const normalizedAnalytes =
      newAnalytes.map(
        (analyte, index) => ({
          ...analyte,
          code:
            analyte.code
              .trim()
              .toUpperCase(),
          name:
            analyte.name.trim(),
          unit:
            analyte.unit?.trim() || null,
          reference_text:
            analyte.reference_text?.trim() ||
            null,
          display_order:
            index,
        }),
      )

    const seenCodes =
      new Set<string>()

    for (
      let index = 0;
      index < normalizedAnalytes.length;
      index += 1
    ) {
      const analyte =
        normalizedAnalytes[index]

      if (!analyte.code) {
        setError(
          `Analyte ${index + 1}: code is required.`,
        )
        return
      }

      if (!analyte.name) {
        setError(
          `Analyte '${analyte.code}': name is required.`,
        )
        return
      }

      if (
        seenCodes.has(
          analyte.code,
        )
      ) {
        setError(
          `Duplicate analyte code '${analyte.code}'.`,
        )
        return
      }

      seenCodes.add(
        analyte.code,
      )

      const referenceLow =
        analyte.reference_low ?? null

      const referenceHigh =
        analyte.reference_high ?? null

      if (
        referenceLow !== null &&
        referenceHigh !== null &&
        referenceLow > referenceHigh
      ) {
        setError(
          `Analyte '${analyte.code}': lower reference cannot exceed upper reference.`,
        )
        return
      }

      if (
        analyte.data_type === 'CODED' &&
        !analyte.options?.length
      ) {
        setError(
          `Analyte '${analyte.code}': add at least one option for a coded result.`,
        )
        return
      }
    }

    setCreatingTest(true)
    setError(null)
    setSuccess(null)

    try {
      const created =
        await createLaboratoryTest(
          accessToken,
          {
            code,
            name,
            specimen:
              specimen || null,
            description:
              description || null,
            analytes:
              normalizedAnalytes,
          },
        )

      setTests(current =>
        [...current, created].sort(
          (a, b) =>
            a.name.localeCompare(
              b.name,
            ),
        ),
      )

      setSelectedTestCode(
        created.code,
      )

      setSuccess(
        `${created.name} created successfully.`,
      )

      resetCreateForm()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to create laboratory investigation.',
      )
    } finally {
      setCreatingTest(false)
    }
  }


  async function saveNewAnalyte(
    form: HTMLFormElement,
  ) {
    if (!selectedTest) {
      return
    }

    setSavingNewAnalyte(true)
    setError(null)
    setSuccess(null)

    const formData = new FormData(form)

    const code = String(
      formData.get('code') ?? '',
    ).trim().toUpperCase()

    const name = String(
      formData.get('name') ?? '',
    ).trim()

    const dataType =
      String(
        formData.get('data_type') ?? 'NUMERIC',
      ) as CreateLaboratoryAnalyteRequest['data_type']

    const unit = String(
      formData.get('unit') ?? '',
    ).trim()

    const lowRaw = String(
      formData.get('reference_low') ?? '',
    ).trim()

    const highRaw = String(
      formData.get('reference_high') ?? '',
    ).trim()

    const referenceText = String(
      formData.get('reference_text') ?? '',
    ).trim()

    const required =
      formData.get('required') === 'on'

    const referenceLow =
      lowRaw === ''
        ? null
        : Number(lowRaw)

    const referenceHigh =
      highRaw === ''
        ? null
        : Number(highRaw)

    if (!code) {
      setError('Analyte code is required.')
      setSavingNewAnalyte(false)
      return
    }

    if (!name) {
      setError('Analyte name is required.')
      setSavingNewAnalyte(false)
      return
    }

    if (
      (lowRaw !== '' &&
        !Number.isFinite(referenceLow)) ||
      (highRaw !== '' &&
        !Number.isFinite(referenceHigh))
    ) {
      setError(
        'Reference values must be valid numbers.',
      )
      setSavingNewAnalyte(false)
      return
    }

    if (
      referenceLow !== null &&
      referenceHigh !== null &&
      referenceLow > referenceHigh
    ) {
      setError(
        'Lower reference cannot exceed upper reference.',
      )
      setSavingNewAnalyte(false)
      return
    }

    if (
      dataType === 'CODED'
    ) {
      setError(
        'Coded analytes should be configured with options. '
        + 'This form currently supports numeric, text, and boolean analytes.',
      )
      setSavingNewAnalyte(false)
      return
    }

    try {
      const created =
        await createLaboratoryAnalyte(
          accessToken,
          selectedTest.code,
          {
            code,
            name,
            data_type: dataType,
            unit: unit || null,
            reference_low: referenceLow,
            reference_high: referenceHigh,
            reference_text:
              referenceText || null,
            options: null,
            required,
            display_order:
              selectedTest.analytes.length,
          },
        )

      setTests(current =>
        current.map(test =>
          test.code !== selectedTest.code
            ? test
            : {
                ...test,
                analytes: [
                  ...test.analytes,
                  created,
                ],
              },
        ),
      )

      setAddingAnalyte(false)

      setSuccess(
        `${created.name} added successfully.`,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to add laboratory analyte.',
      )
    } finally {
      setSavingNewAnalyte(false)
    }
  }


  async function saveAnalyte(
    analyte: LaboratoryTestAnalyte,
    form: HTMLFormElement,
  ) {
    setSavingAnalyteId(analyte.id)
    setError(null)
    setSuccess(null)

    const formData =
      new FormData(form)

    const lowRaw =
      String(
        formData.get('reference_low') ?? '',
      ).trim()

    const highRaw =
      String(
        formData.get('reference_high') ?? '',
      ).trim()

    const referenceText =
      String(
        formData.get('reference_text') ?? '',
      ).trim()

    const unit =
      String(
        formData.get('unit') ?? '',
      ).trim()

    const name =
      String(
        formData.get('name') ?? '',
      ).trim()

    const required =
      formData.get('required') === 'on'

    const referenceLow =
      lowRaw === ''
        ? null
        : Number(lowRaw)

    const referenceHigh =
      highRaw === ''
        ? null
        : Number(highRaw)

    if (
      (lowRaw !== '' &&
        !Number.isFinite(referenceLow)) ||
      (highRaw !== '' &&
        !Number.isFinite(referenceHigh))
    ) {
      setError(
        `${analyte.name}: reference values must be valid numbers.`,
      )
      setSavingAnalyteId(null)
      return
    }

    if (
      referenceLow !== null &&
      referenceHigh !== null &&
      referenceLow > referenceHigh
    ) {
      setError(
        `${analyte.name}: lower reference cannot exceed upper reference.`,
      )
      setSavingAnalyteId(null)
      return
    }

    try {
      const updated =
        await updateLaboratoryAnalyte(
          accessToken,
          selectedTestCode,
          analyte.id,
          {
            name,
            unit:
              unit || null,
            reference_low:
              referenceLow,
            reference_high:
              referenceHigh,
            reference_text:
              referenceText || null,
            required,
          },
        )

      setTests(
        current =>
          current.map(
            test =>
              test.code !==
              selectedTestCode
                ? test
                : {
                    ...test,
                    analytes:
                      test.analytes.map(
                        candidate =>
                          candidate.id ===
                          updated.id
                            ? updated
                            : candidate,
                      ),
                  },
          ),
      )

      setSuccess(
        `${updated.name} updated successfully.`,
      )

      setEditingAnalyteId(null)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to update laboratory analyte.',
      )
    } finally {
      setSavingAnalyteId(null)
    }
  }


  return (
    <section className="admin-laboratory-catalogue">

      {/* ================================================================== */}
      {/* Header                                                             */}
      {/* ================================================================== */}

      <div className="page-header">

        <div>
          <p className="eyebrow">
            CLINICAL CONFIGURATION
          </p>

          <h2>
            Laboratory Catalogue
          </h2>

          <p>
            Maintain investigations, analytes,
            and laboratory reference information.
          </p>
        </div>

        <div className="page-header-actions">

          <span className="staff-directory-count">
            {tests.length}{' '}
            {tests.length === 1
              ? 'investigation'
              : 'investigations'}
          </span>

          <button
            type="button"
            className="primary-button"
            onClick={() => {
              if (showCreateForm) {
                resetCreateForm()
                return
              }

              setShowCreateForm(true)
              setError(null)
              setSuccess(null)
            }}
            disabled={creatingTest}
          >
            {showCreateForm
              ? 'Cancel'
              : 'New Investigation'}
          </button>

        </div>

      </div>


      {/* ================================================================== */}
      {/* Feedback                                                           */}
      {/* ================================================================== */}

      {error && (
        <div className="error-state">
          {error}
        </div>
      )}

      {success && (
        <div className="success-state">
          {success}
        </div>
      )}


      {showCreateForm && (
        <section className="workspace-panel">

          <div className="panel-header">

            <div>
              <p className="eyebrow">
                NEW INVESTIGATION
              </p>

              <h3>
                Create laboratory investigation
              </h3>

              <p>
                Define the investigation and all of
                the analytes used to record its results.
              </p>
            </div>

          </div>


          <form
            className="shared-form-section"
            onSubmit={handleCreateTest}
          >

            <div className="form-grid">

              <div className="form-field">
                <label>
                  Investigation name
                </label>

                <input
                  className="form-control"
                  value={newTestName}
                  onChange={event =>
                    setNewTestName(
                      event.target.value,
                    )
                  }
                  placeholder="e.g. Full Blood Count"
                  disabled={creatingTest}
                />
              </div>


              <div className="form-field">
                <label>
                  Investigation code
                </label>

                <input
                  className="form-control"
                  value={newTestCode}
                  onChange={event =>
                    setNewTestCode(
                      event.target.value.toUpperCase(),
                    )
                  }
                  placeholder="e.g. CBC"
                  disabled={creatingTest}
                />
              </div>


              <div className="form-field">
                <label>
                  Specimen
                </label>

                <input
                  className="form-control"
                  value={newTestSpecimen}
                  onChange={event =>
                    setNewTestSpecimen(
                      event.target.value,
                    )
                  }
                  placeholder="e.g. EDTA blood"
                  disabled={creatingTest}
                />
              </div>


              <div className="
                form-field
                form-field--full
              ">
                <label>
                  Description
                </label>

                <textarea
                  className="form-control"
                  value={newTestDescription}
                  onChange={event =>
                    setNewTestDescription(
                      event.target.value,
                    )
                  }
                  placeholder="Describe the investigation..."
                  rows={3}
                  disabled={creatingTest}
                />
              </div>

            </div>


            <div className="
              laboratory-create-analytes
            ">

              <div className="section-heading">

                <div>
                  <h3>
                    Analytes
                  </h3>

                  <p>
                    Add every result field that
                    belongs to this investigation.
                  </p>
                </div>

                <button
                  type="button"
                  className="secondary-button"
                  onClick={addNewAnalyte}
                  disabled={creatingTest}
                >
                  + Add analyte
                </button>

              </div>


              {newAnalytes.length === 0 ? (
                <div className="empty-state">
                  <strong>
                    No analytes added yet.
                  </strong>

                  <p>
                    Add at least one analyte before
                    creating the investigation.
                  </p>
                </div>
              ) : (
                <div className="
                  laboratory-create-analyte-list
                ">

                  {newAnalytes.map(
                    (analyte, index) => (
                      <article
                        key={index}
                        className="
                          laboratory-create-analyte-card
                        "
                      >

                        <div className="
                          laboratory-create-analyte-heading
                        ">

                          <strong>
                            Analyte {index + 1}
                          </strong>

                          <button
                            type="button"
                            className="danger-button"
                            onClick={() =>
                              removeNewAnalyte(
                                index,
                              )
                            }
                            disabled={creatingTest}
                          >
                            Remove
                          </button>

                        </div>


                        <div className="form-grid">

                          <div className="form-field">
                            <label>
                              Display name
                            </label>

                            <input
                              className="form-control"
                              value={analyte.name}
                              onChange={event =>
                                updateNewAnalyte(
                                  index,
                                  {
                                    name:
                                      event.target.value,
                                  },
                                )
                              }
                              placeholder="e.g. Haemoglobin"
                              disabled={creatingTest}
                            />
                          </div>


                          <div className="form-field">
                            <label>
                              Code
                            </label>

                            <input
                              className="form-control"
                              value={analyte.code}
                              onChange={event =>
                                updateNewAnalyte(
                                  index,
                                  {
                                    code:
                                      event.target.value.toUpperCase(),
                                  },
                                )
                              }
                              placeholder="e.g. HB"
                              disabled={creatingTest}
                            />
                          </div>


                          <div className="form-field">
                            <label>
                              Data type
                            </label>

                            <select
                              className="form-control"
                              value={analyte.data_type}
                              onChange={event => {
                                const dataType =
                                  event.target.value as LaboratoryAnalyteDataType

                                updateNewAnalyte(
                                  index,
                                  {
                                    data_type:
                                      dataType,
                                    options:
                                      dataType ===
                                      'CODED'
                                        ? analyte.options ??
                                          ['']
                                        : null,
                                    reference_low:
                                      dataType ===
                                      'NUMERIC'
                                        ? analyte.reference_low ??
                                          null
                                        : null,
                                    reference_high:
                                      dataType ===
                                      'NUMERIC'
                                        ? analyte.reference_high ??
                                          null
                                        : null,
                                  },
                                )
                              }}
                              disabled={creatingTest}
                            >
                              <option value="NUMERIC">
                                Numeric
                              </option>

                              <option value="TEXT">
                                Text
                              </option>

                              <option value="BOOLEAN">
                                Boolean
                              </option>

                              <option value="CODED">
                                Coded
                              </option>
                            </select>
                          </div>


                          <div className="form-field">
                            <label>
                              Unit
                            </label>

                            <input
                              className="form-control"
                              value={
                                analyte.unit ??
                                ''
                              }
                              onChange={event =>
                                updateNewAnalyte(
                                  index,
                                  {
                                    unit:
                                      event.target.value,
                                  },
                                )
                              }
                              placeholder="e.g. g/dL"
                              disabled={creatingTest}
                            />
                          </div>


                          {analyte.data_type ===
                            'NUMERIC' && (
                            <>

                              <div className="form-field">
                                <label>
                                  Reference low
                                </label>

                                <input
                                  className="form-control"
                                  type="number"
                                  step="any"
                                  value={
                                    analyte.reference_low ??
                                    ''
                                  }
                                  onChange={event =>
                                    updateNewAnalyte(
                                      index,
                                      {
                                        reference_low:
                                          event.target.value ===
                                          ''
                                            ? null
                                            : Number(
                                                event.target.value,
                                              ),
                                      },
                                    )
                                  }
                                  disabled={creatingTest}
                                />
                              </div>


                              <div className="form-field">
                                <label>
                                  Reference high
                                </label>

                                <input
                                  className="form-control"
                                  type="number"
                                  step="any"
                                  value={
                                    analyte.reference_high ??
                                    ''
                                  }
                                  onChange={event =>
                                    updateNewAnalyte(
                                      index,
                                      {
                                        reference_high:
                                          event.target.value ===
                                          ''
                                            ? null
                                            : Number(
                                                event.target.value,
                                              ),
                                      },
                                    )
                                  }
                                  disabled={creatingTest}
                                />
                              </div>

                            </>
                          )}


                          {(analyte.data_type ===
                            'NUMERIC' ||
                            analyte.data_type ===
                              'TEXT') && (
                            <div className="
                              form-field
                              form-field--full
                            ">

                              <label>
                                Reference text
                              </label>

                              <input
                                className="form-control"
                                value={
                                  analyte.reference_text ??
                                  ''
                                }
                                onChange={event =>
                                  updateNewAnalyte(
                                    index,
                                    {
                                      reference_text:
                                        event.target.value,
                                    },
                                  )
                                }
                                placeholder="Optional laboratory reference note"
                                disabled={creatingTest}
                              />

                            </div>
                          )}

                        </div>


                        {analyte.data_type ===
                          'CODED' && (
                          <div className="
                            laboratory-coded-options
                          ">

                            <div className="
                              section-heading
                            ">

                              <div>
                                <strong>
                                  Result options
                                </strong>

                                <p>
                                  Define the values the
                                  laboratory can select.
                                </p>
                              </div>

                              <button
                                type="button"
                                className="secondary-button"
                                onClick={() =>
                                  updateNewAnalyte(
                                    index,
                                    {
                                      options: [
                                        ...(analyte.options ??
                                          []),
                                        '',
                                      ],
                                    },
                                  )
                                }
                                disabled={creatingTest}
                              >
                                + Add option
                              </button>

                            </div>


                            <div className="
                              laboratory-option-list
                            ">

                              {(analyte.options ??
                                ['']).map(
                                (
                                  option,
                                  optionIndex,
                                ) => (
                                  <div
                                    key={
                                      optionIndex
                                    }
                                    className="
                                      laboratory-option-row
                                    "
                                  >

                                    <input
                                      className="form-control"
                                      value={option}
                                      onChange={event => {
                                        const options = [
                                          ...(analyte.options ??
                                            []),
                                        ]

                                        options[
                                          optionIndex
                                        ] =
                                          event.target.value

                                        updateNewAnalyte(
                                          index,
                                          { options },
                                        )
                                      }}
                                      placeholder="e.g. Positive"
                                      disabled={creatingTest}
                                    />

                                    <button
                                      type="button"
                                      className="danger-button"
                                      onClick={() => {
                                        const options =
                                          (
                                            analyte.options ??
                                            []
                                          ).filter(
                                            (
                                              _,
                                              candidateIndex,
                                            ) =>
                                              candidateIndex !==
                                              optionIndex,
                                          )

                                        updateNewAnalyte(
                                          index,
                                          {
                                            options:
                                              options.length
                                                ? options
                                                : [''],
                                          },
                                        )
                                      }}
                                      disabled={creatingTest}
                                    >
                                      Remove
                                    </button>

                                  </div>
                                ),
                              )}

                            </div>

                          </div>
                        )}


                        <label className="
                          laboratory-required-toggle
                        ">

                          <input
                            type="checkbox"
                            checked={
                              analyte.required ??
                              false
                            }
                            onChange={event =>
                              updateNewAnalyte(
                                index,
                                {
                                  required:
                                    event.target.checked,
                                },
                              )
                            }
                            disabled={creatingTest}
                          />

                          <span>
                            Required for final result
                          </span>

                        </label>

                      </article>
                    ),
                  )}

                </div>
              )}

            </div>


            <div className="form-actions">

              <button
                type="button"
                className="secondary-button"
                onClick={resetCreateForm}
                disabled={creatingTest}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="primary-button"
                disabled={
                  creatingTest ||
                  newAnalytes.length === 0
                }
              >
                {creatingTest
                  ? 'Creating...'
                  : 'Create Investigation'}
              </button>

            </div>

          </form>

        </section>
      )}


      {/* ================================================================== */}
      {/* Catalogue                                                           */}
      {/* ================================================================== */}

      {loading ? (
        <div className="workspace-panel empty-state">
          <strong>
            Loading laboratory catalogue...
          </strong>
        </div>
      ) : tests.length === 0 ? (
        <div className="workspace-panel empty-state">
          <strong>
            No laboratory investigations found.
          </strong>

          <p>
            The laboratory catalogue has not been
            configured yet.
          </p>
        </div>
      ) : (
        <div className="laboratory-catalogue-layout">

          {/* ================================================================ */}
          {/* Investigation List                                                */}
          {/* ================================================================ */}

          <section className="
            workspace-panel
            laboratory-investigation-list
          ">

            <div className="panel-header">

              <div>
                <p className="eyebrow">
                  INVESTIGATIONS
                </p>

                <h3>
                  Laboratory tests
                </h3>

                <p>
                  Select an investigation to configure
                  its analytes.
                </p>
              </div>

              <span className="staff-directory-count">
                {filteredTests.length} shown
              </span>

            </div>


            <div className="laboratory-investigation-search">

              <input
                type="search"
                className="form-control"
                value={searchQuery}
                onChange={event =>
                  setSearchQuery(
                    event.target.value,
                  )
                }
                placeholder="Search investigation..."
                aria-label="Search laboratory investigations"
              />

            </div>


            {filteredTests.length === 0 ? (
              <div className="empty-state">
                <strong>
                  No matching investigations.
                </strong>

                <p>
                  Try the investigation name or code.
                </p>
              </div>
            ) : (
              <div className="laboratory-investigation-items">

                {filteredTests.map(test => (
                  <button
                    key={test.code}
                    type="button"
                    className={
                      test.code === selectedTestCode
                        ? 'laboratory-investigation-item active'
                        : 'laboratory-investigation-item'
                    }
                    onClick={() => {
                      setSelectedTestCode(
                        test.code,
                      )
                      setEditingAnalyteId(null)
                      setError(null)
                      setSuccess(null)
                    }}
                  >

                    <span>
                      <strong>
                        {test.name}
                      </strong>

                      <small>
                        {test.code}
                        {' · '}
                        {test.analytes.length}{' '}
                        {test.analytes.length === 1
                          ? 'analyte'
                          : 'analytes'}
                      </small>
                    </span>

                    <span className="laboratory-investigation-arrow">
                      →
                    </span>

                  </button>
                ))}

              </div>
            )}

          </section>


          {/* ================================================================ */}
          {/* Investigation Detail                                               */}
          {/* ================================================================ */}

          <section className="
            workspace-panel
            laboratory-investigation-detail
          ">

            {!selectedTest ? (
              <div className="empty-state">
                <strong>
                  Select an investigation.
                </strong>

                <p>
                  Choose an investigation from the
                  list to view its analytes.
                </p>
              </div>
            ) : (
              <>

                <div className="panel-header">

                  <div>
                    <p className="eyebrow">
                      SELECTED INVESTIGATION
                    </p>

                    <h3>
                      {selectedTest.name}
                    </h3>

                    <p>
                      {selectedTest.code}
                      {' · '}
                      Specimen:{' '}
                      {selectedTest.specimen ??
                        'Not specified'}
                    </p>
                  </div>

                  <span
                    className={
                      selectedTest.active
                        ? 'status-badge status-badge--active'
                        : 'status-badge status-badge--inactive'
                    }
                  >
                    {selectedTest.active
                      ? 'Active'
                      : 'Inactive'}
                  </span>

                </div>


                {selectedTest.description && (
                  <div className="laboratory-investigation-description">
                    {selectedTest.description}
                  </div>
                )}


                <div className="
                  laboratory-analyte-section
                ">

                  <div className="section-heading">

                    <div>
                      <h3>
                        Analytes
                      </h3>

                      <p>
                        Configure how results for this
                        investigation are recorded.
                      </p>
                    </div>

                    <div className="laboratory-analyte-heading-actions">

                      <span className="staff-directory-count">
                        {selectedTest.analytes.length}
                      </span>

                      <button
                        type="button"
                        className="secondary-button"
                        onClick={() => {
                          setAddingAnalyte(
                            current => !current,
                          )
                          setEditingAnalyteId(null)
                          setError(null)
                          setSuccess(null)
                        }}
                        disabled={savingNewAnalyte}
                      >
                        {addingAnalyte
                          ? 'Close'
                          : '+ Add analyte'}
                      </button>

                    </div>

                  </div>


                  {addingAnalyte && (
                    <form
                      className="laboratory-analyte-edit-form"
                      onSubmit={event => {
                        event.preventDefault()

                        void saveNewAnalyte(
                          event.currentTarget,
                        )
                      }}
                    >

                      <div className="form-grid">

                        <div className="form-field">
                          <label>
                            Analyte name
                          </label>

                          <input
                            name="name"
                            className="form-control"
                            placeholder="e.g. White Blood Cell Count"
                            required
                            disabled={savingNewAnalyte}
                          />
                        </div>


                        <div className="form-field">
                          <label>
                            Analyte code
                          </label>

                          <input
                            name="code"
                            className="form-control"
                            placeholder="e.g. WBC"
                            required
                            disabled={savingNewAnalyte}
                          />
                        </div>


                        <div className="form-field">
                          <label>
                            Data type
                          </label>

                          <select
                            name="data_type"
                            className="form-control"
                            defaultValue="NUMERIC"
                            disabled={savingNewAnalyte}
                          >
                            <option value="NUMERIC">
                              Numeric
                            </option>

                            <option value="TEXT">
                              Text
                            </option>

                            <option value="BOOLEAN">
                              Yes / No
                            </option>
                          </select>
                        </div>


                        <div className="form-field">
                          <label>
                            Unit
                          </label>

                          <input
                            name="unit"
                            className="form-control"
                            placeholder="e.g. × 10⁹/L"
                            disabled={savingNewAnalyte}
                          />
                        </div>


                        <div className="form-field">
                          <label>
                            Reference low
                          </label>

                          <input
                            name="reference_low"
                            type="number"
                            step="any"
                            className="form-control"
                            disabled={savingNewAnalyte}
                          />
                        </div>


                        <div className="form-field">
                          <label>
                            Reference high
                          </label>

                          <input
                            name="reference_high"
                            type="number"
                            step="any"
                            className="form-control"
                            disabled={savingNewAnalyte}
                          />
                        </div>


                        <div className="form-field form-field--full">
                          <label>
                            Reference text
                          </label>

                          <input
                            name="reference_text"
                            className="form-control"
                            placeholder="Optional reference information"
                            disabled={savingNewAnalyte}
                          />
                        </div>


                        <label className="laboratory-required-toggle">
                          <input
                            name="required"
                            type="checkbox"
                            disabled={savingNewAnalyte}
                          />

                          <span>
                            Required for final result
                          </span>
                        </label>

                      </div>


                      <div className="admin-laboratory-analyte-actions">

                        <button
                          type="button"
                          className="secondary-button"
                          onClick={() =>
                            setAddingAnalyte(false)
                          }
                          disabled={savingNewAnalyte}
                        >
                          Cancel
                        </button>

                        <button
                          type="submit"
                          className="primary-button"
                          disabled={savingNewAnalyte}
                        >
                          {savingNewAnalyte
                            ? 'Adding...'
                            : 'Add analyte'}
                        </button>

                      </div>

                    </form>
                  )}


                  {selectedTest.analytes.length === 0 ? (
                    <div className="empty-state">
                      <strong>
                        No analytes configured.
                      </strong>

                      <p>
                        This investigation has no
                        analyte definitions yet.
                      </p>
                    </div>
                  ) : (
                    <div className="
                      laboratory-analyte-list
                    ">

                      {selectedTest.analytes.map(
                        analyte => {

                          const isEditing =
                            editingAnalyteId ===
                            analyte.id

                          return (
                            <article
                              key={analyte.id}
                              className={
                                isEditing
                                  ? 'laboratory-analyte-card editing'
                                  : 'laboratory-analyte-card'
                              }
                            >

                              <div className="
                                laboratory-analyte-summary
                              ">

                                <div>
                                  <strong>
                                    {analyte.name}
                                  </strong>

                                  <span>
                                    {analyte.code}
                                    {' · '}
                                    {analyte.data_type}
                                  </span>
                                </div>


                                <div className="
                                  laboratory-analyte-reference
                                ">

                                  <span>
                                    {analyte.unit ??
                                      'No unit'}
                                  </span>

                                  <span>
                                    {analyte.reference_low !== null &&
                                    analyte.reference_high !== null
                                      ? `${analyte.reference_low}–${analyte.reference_high}`
                                      : analyte.reference_text ??
                                        'No reference interval'}
                                  </span>

                                  {analyte.required && (
                                    <span className="
                                      status-badge
                                      status-badge--active
                                    ">
                                      Required
                                    </span>
                                  )}

                                </div>


                                <button
                                  type="button"
                                  className="secondary-button"
                                  onClick={() =>
                                    setEditingAnalyteId(
                                      isEditing
                                        ? null
                                        : analyte.id,
                                    )
                                  }
                                >
                                  {isEditing
                                    ? 'Close'
                                    : 'Edit reference'}
                                </button>

                              </div>


                              {isEditing && (
                                <form
                                  className="
                                    laboratory-analyte-edit-form
                                  "
                                  onSubmit={event => {
                                    event.preventDefault()

                                    void saveAnalyte(
                                      analyte,
                                      event.currentTarget,
                                    )
                                  }}
                                >

                                  <div className="form-grid">

                                    <div className="form-field">
                                      <label>
                                        Display name
                                      </label>

                                      <input
                                        name="name"
                                        className="form-control"
                                        defaultValue={
                                          analyte.name
                                        }
                                      />
                                    </div>


                                    <div className="form-field">
                                      <label>
                                        Unit
                                      </label>

                                      <input
                                        name="unit"
                                        className="form-control"
                                        defaultValue={
                                          analyte.unit ??
                                          ''
                                        }
                                        placeholder="e.g. mmol/L"
                                      />
                                    </div>


                                    <div className="form-field">
                                      <label>
                                        Reference low
                                      </label>

                                      <input
                                        name="reference_low"
                                        className="form-control"
                                        type="number"
                                        step="any"
                                        defaultValue={
                                          analyte.reference_low ??
                                          ''
                                        }
                                      />
                                    </div>


                                    <div className="form-field">
                                      <label>
                                        Reference high
                                      </label>

                                      <input
                                        name="reference_high"
                                        className="form-control"
                                        type="number"
                                        step="any"
                                        defaultValue={
                                          analyte.reference_high ??
                                          ''
                                        }
                                      />
                                    </div>


                                    <div className="
                                      form-field
                                      form-field--full
                                    ">
                                      <label>
                                        Reference text
                                      </label>

                                      <input
                                        name="reference_text"
                                        className="form-control"
                                        defaultValue={
                                          analyte.reference_text ??
                                          ''
                                        }
                                        placeholder="e.g. laboratory-specific interval"
                                      />
                                    </div>

                                  </div>


                                  <div className="
                                    laboratory-required-toggle
                                  ">
                                    <label>
                                      <input
                                        name="required"
                                        type="checkbox"
                                        defaultChecked={
                                          analyte.required
                                        }
                                      />

                                      <span>
                                        Required for final result
                                      </span>
                                    </label>
                                  </div>


                                  <div className="form-actions">

                                    <button
                                      type="button"
                                      className="secondary-button"
                                      onClick={() =>
                                        setEditingAnalyteId(
                                          null,
                                        )
                                      }
                                      disabled={
                                        savingAnalyteId ===
                                        analyte.id
                                      }
                                    >
                                      Cancel
                                    </button>

                                    <button
                                      type="submit"
                                      className="primary-button"
                                      disabled={
                                        savingAnalyteId ===
                                        analyte.id
                                      }
                                    >
                                      {savingAnalyteId ===
                                      analyte.id
                                        ? 'Saving...'
                                        : 'Save Changes'}
                                    </button>

                                  </div>

                                </form>
                              )}

                            </article>
                          )
                        },
                      )}

                    </div>
                  )}

                </div>

              </>
            )}

          </section>

        </div>
      )}

    </section>
  )
}
