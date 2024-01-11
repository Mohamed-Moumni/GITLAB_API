/** @odoo-module **/

import fieldUtils from 'web.field_utils';
import PlanningGanttRow from 'planning.PlanningGanttRow';

const KZMPlanningGanttRow = PlanningGanttRow.include({
     _getAggregateGroupedPillsDisplayName(pill) {
        const totalAllocatedHours = pill.aggregatedPills.reduce((acc, val) => acc + val.allocated_hours, 0).toFixed(2);
        return fieldUtils.format.float_time(totalAllocatedHours);
    },

      _isPillsInInterval(pill, intervalStart, intervalStop) {
        return pill.startDate < intervalStop && pill.stopDate > intervalStart;
    },

});

export default KZMPlanningGanttRow;
