from .models import LeadStatus

class LifecycleManager:
    """
    Enforces the transition logic for the Lead Lifecycle.
    """
    
    @staticmethod
    def can_transition(current_status, new_status):
        # Define allowed next steps
        valid_transitions = {
            LeadStatus.SUSPECT: [LeadStatus.TARGET],
            LeadStatus.TARGET: [LeadStatus.PROSPECT, LeadStatus.SUSPECT], # Can fail back to suspect
            LeadStatus.PROSPECT: [LeadStatus.QUALIFIED, LeadStatus.SUSPECT],
            LeadStatus.QUALIFIED: [LeadStatus.CLIENT, LeadStatus.SUSPECT],
            LeadStatus.CLIENT: [] # End state
        }
        
        return new_status in valid_transitions.get(current_status, [])

    @staticmethod
    def validate_quality_gate(entity):
        """
        The 'Deterioration Sensor' Logic Check.
        Prevents promotion to QUALIFIED if risk factors are high.
        """
        if entity.financial_covenants_active:
             # If covenants are active, we need manual verification before Qualifying.
             # This returns a block signal.
             return False, "BLOCKED: Entity has active Financial Covenants. Manual Audit Required."
        
        return True, "PASSED"
