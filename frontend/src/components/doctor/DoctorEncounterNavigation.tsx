interface DoctorEncounterNavigationProps {
  onBackToQueue: () => void
}

export default function DoctorEncounterNavigation({
  onBackToQueue,
}: DoctorEncounterNavigationProps) {
  return (
    <section className="doctor-encounter-navigation">
      <button
        type="button"
        className="secondary-button doctor-back-to-queue"
        onClick={onBackToQueue}
      >
        <span aria-hidden="true">←</span>
        Back to Doctor Queue
      </button>
    </section>
  )
}
