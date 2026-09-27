import type { ComponentProps } from 'react'

import type { ClinicalDocument } from '../../api/clinicalDocuments'
import type { Episode } from '../../api/episodes'
import type { Encounter } from '../../api/encounters'

import InitialClerkingPanel from './InitialClerkingPanel'
import ProgressNotePanel from './ProgressNotePanel'
import SignedClinicalDocumentSummary from './SignedClinicalDocumentSummary'
import type { useDoctorDocumentation } from './useDoctorDocumentation'

type ProgressNoteProps =
  ComponentProps<typeof ProgressNotePanel>

interface Props {
  documentation: ReturnType<typeof useDoctorDocumentation>
  progressNote: ClinicalDocument | null
  selectedEncounter: Encounter
  selectedEpisode: Episode | null
  loadingProgressNote: boolean
  savingProgressNote: boolean
  signingProgressNote: boolean
  admittingEpisode: boolean

  vitalsCount: number
  insertLatestVitals: ProgressNoteProps['onInsertLatestVitals']
  saveProgressNote: () => Promise<void>
  signProgressNote: () => Promise<void>
  admitSelectedEpisode: () => Promise<void>
}

export default function DoctorDocumentationPanel({
  documentation,
  progressNote,
  selectedEncounter,
  selectedEpisode,
  loadingProgressNote,
  savingProgressNote,
  signingProgressNote,
  admittingEpisode,
  vitalsCount,
  insertLatestVitals,
  saveProgressNote,
  signProgressNote,
  admitSelectedEpisode,
}: Props) {
  return (
    <div className="doctor-documentation-section">
      <div className="doctor-section-heading">
        <p className="eyebrow">DOCUMENTATION</p>
        <h2>Clinical Documentation</h2>
        <p>Record and review the current clinical documentation.</p>
      </div>

      {documentation.doctorNoteDocumentType() === 'INITIAL_CLERKING' ? (
        <InitialClerkingPanel
          document={progressNote}
          loading={loadingProgressNote}
          saving={savingProgressNote}
          signing={signingProgressNote}
          complaint={documentation.initialClerking.complaint}
          complaintDuration={documentation.initialClerking.complaintDuration}
          history={documentation.initialClerking.history}
          reviewOfSystems={documentation.initialClerking.reviewOfSystems}
          pastMedicalHistory={documentation.initialClerking.pastMedicalHistory}
          pastSurgicalHistory={documentation.initialClerking.pastSurgicalHistory}
          drugHistory={documentation.initialClerking.drugHistory}
          allergies={documentation.initialClerking.allergies}
          familyHistory={documentation.initialClerking.familyHistory}
          socialHistory={documentation.initialClerking.socialHistory}
          personalHistory={documentation.initialClerking.personalHistory}
          ideas={documentation.initialClerking.ideas}
          concerns={documentation.initialClerking.concerns}
          expectations={documentation.initialClerking.expectations}
          examGeneral={documentation.initialClerking.examGeneral}
          examCardiovascular={documentation.initialClerking.examCardiovascular}
          examRespiratory={documentation.initialClerking.examRespiratory}
          examAbdomen={documentation.initialClerking.examAbdomen}
          examNeurological={documentation.initialClerking.examNeurological}
          examMusculoskeletal={documentation.initialClerking.examMusculoskeletal}
          examGenitourinary={documentation.initialClerking.examGenitourinary}
          examOther={documentation.initialClerking.examOther}
          onComplaintChange={value => documentation.updateInitialClerking('complaint', value)}
          onComplaintDurationChange={value => documentation.updateInitialClerking('complaintDuration', value)}
          onHistoryChange={value => documentation.updateInitialClerking('history', value)}
          onReviewOfSystemsChange={value => documentation.updateInitialClerking('reviewOfSystems', value)}
          onPastMedicalHistoryChange={value => documentation.updateInitialClerking('pastMedicalHistory', value)}
          onPastSurgicalHistoryChange={value => documentation.updateInitialClerking('pastSurgicalHistory', value)}
          onDrugHistoryChange={value => documentation.updateInitialClerking('drugHistory', value)}
          onAllergiesChange={value => documentation.updateInitialClerking('allergies', value)}
          onFamilyHistoryChange={value => documentation.updateInitialClerking('familyHistory', value)}
          onSocialHistoryChange={value => documentation.updateInitialClerking('socialHistory', value)}
          onPersonalHistoryChange={value => documentation.updateInitialClerking('personalHistory', value)}
          onIdeasChange={value => documentation.updateInitialClerking('ideas', value)}
          onConcernsChange={value => documentation.updateInitialClerking('concerns', value)}
          onExpectationsChange={value => documentation.updateInitialClerking('expectations', value)}
          onExamGeneralChange={value => documentation.updateInitialClerking('examGeneral', value)}
          onExamCardiovascularChange={value => documentation.updateInitialClerking('examCardiovascular', value)}
          onExamRespiratoryChange={value => documentation.updateInitialClerking('examRespiratory', value)}
          onExamAbdomenChange={value => documentation.updateInitialClerking('examAbdomen', value)}
          onExamNeurologicalChange={value => documentation.updateInitialClerking('examNeurological', value)}
          onExamMusculoskeletalChange={value => documentation.updateInitialClerking('examMusculoskeletal', value)}
          onExamGenitourinaryChange={value => documentation.updateInitialClerking('examGenitourinary', value)}
          onExamOtherChange={value => documentation.updateInitialClerking('examOther', value)}
          onSave={() => void saveProgressNote()}
          onSign={() => void signProgressNote()}
          admitting={admittingEpisode}
          canAdmit={Boolean(
            progressNote &&
            progressNote.document_type === 'INITIAL_CLERKING' &&
            progressNote.status === 'SIGNED' &&
            selectedEpisode?.status === 'OPEN',
          )}
          onAdmit={() => void admitSelectedEpisode()}
        />
      ) : (
        <ProgressNotePanel
          noteTitle="Progress Note"
          progressNote={progressNote}
          encounterClosed={selectedEncounter.status === 'CLOSED'}
          loading={loadingProgressNote}
          saving={savingProgressNote}
          signing={signingProgressNote}
          subjective={documentation.progressNoteForm.subjective}
          objective={documentation.progressNoteForm.objective}
          workingDiagnosis={documentation.progressNoteForm.workingDiagnosis}
          differentials={documentation.progressNoteForm.differentials}
          plan={documentation.progressNoteForm.plan}
          onSubjectiveChange={value => documentation.updateProgressNote('subjective', value)}
          onObjectiveChange={value => documentation.updateProgressNote('objective', value)}
          onWorkingDiagnosisChange={value => documentation.updateProgressNote('workingDiagnosis', value)}
          onDifferentialsChange={value => documentation.updateProgressNote('differentials', value)}
          onPlanChange={value => documentation.updateProgressNote('plan', value)}
          onInsertLatestVitals={insertLatestVitals}
          hasVitals={vitalsCount > 0}
          onSave={() => void saveProgressNote()}
          onSign={() => void signProgressNote()}
        />
      )}

      <SignedClinicalDocumentSummary document={progressNote} />
    </div>
  )
}
