/*  Representing enums

    enums are supported by the Certora Verification Language (CVL), 
    according to thier low level representation - uint8.
    in our case:
        -UNINITIALIZED = 0
        -PENDING = 1
        -STARTED = 2
        -ENDED = 3
        -CANCELLED = 4
    So for exmple if we write 'state == 0' we mean 'state == UNINITIALIZED'
    or 'state % 2 == 1' we mean 'state == PENDING || state == ENDED'.

    We will learn more about supported data structures in future lessons.
    For now, follow the above explanation to pass this exercise.
 */


// Checks that when a meeting is created, the planned end time is greater than the start time

methods{
	function getStateById(uint256 meetingId) external returns (IMeetingScheduler.MeetingStatus) envfree;
	function getnumOfParticipants(uint256) external returns (uint256) envfree;
}

definition isUninitalized() returns IMeetingScheduler.MeetingStatus = IMeetingScheduler.MeetingStatus.UNINITIALIZED;
definition isPending() returns IMeetingScheduler.MeetingStatus = IMeetingScheduler.MeetingStatus.PENDING;
definition isStarted() returns IMeetingScheduler.MeetingStatus = IMeetingScheduler.MeetingStatus.STARTED;
definition isEnded() returns IMeetingScheduler.MeetingStatus = IMeetingScheduler.MeetingStatus.ENDED;
definition isCancelled() returns IMeetingScheduler.MeetingStatus = IMeetingScheduler.MeetingStatus.CANCELLED;



/// Only meeting can be scheduled (PENDING) that have the status UNINITIALIZED before and only by calling scheduleMeeing

rule canOnlyBeScheduledIfUninitalized(method f, env e, calldataarg arg, uint256 meetingId){

IMeetingScheduler.MeetingStatus stateBefore = getStateById(meetingId);

f(e, arg);

IMeetingScheduler.MeetingStatus stateAfter = getStateById(meetingId);

assert stateBefore == isUninitalized() => (stateAfter == isUninitalized() || stateAfter == isPending()), "State must be UNINITIALIZED or PENDING";

assert (stateBefore == isUninitalized() && stateAfter == isPending()) => f.selector == sig:scheduleMeeting(uint256,uint256,uint256).selector;


}

rule startBeforeEnd(method f, calldataarg arg, uint256 meetingId, uint256 startTime, uint256 endTime) {
	env e;
    scheduleMeeting(e, meetingId, startTime, endTime);
	f(e, arg);
    uint256 scheduledStartTime = getStartTimeById(e, meetingId);
    uint256 scheduledEndTime = getEndTimeById(e, meetingId);

	assert scheduledStartTime < scheduledEndTime, "the created meeting's start time is not before its end time";
}


// Checks that a meeting can only be started within the defined range [startTime, endTime]
rule startOnTime(method f, uint256 meetingId) {
	env e;
	calldataarg args;
	IMeetingScheduler.MeetingStatus stateBefore = getStateById(e, meetingId);
	f(e, args); // call only non reverting paths to any function on any arguments.
	IMeetingScheduler.MeetingStatus stateAfter = getStateById(e, meetingId);
    uint256 startTimeAfter = getStartTimeById(e, meetingId);
    uint256 endTimeAfter = getEndTimeById(e, meetingId);
    
	assert (stateBefore == isPending() && stateAfter == isStarted()) => startTimeAfter <= e.block.timestamp, "started a meeting before the designated starting time.";
	assert (stateBefore == isPending() && stateAfter == isStarted()) => endTimeAfter > e.block.timestamp, "started a meeting after the designated end time.";
	
}


// Checks that state transition from STARTED to ENDED can only happen if endMeeting() was called
// @note read again the comment at the top regarding f.selector
rule checkStartedToStateTransition(method f, uint256 meetingId) {
	env e;
	calldataarg args;
	IMeetingScheduler.MeetingStatus stateBefore = getStateById(e, meetingId);
	f(e, args);
    IMeetingScheduler.MeetingStatus stateAfter = getStateById(e, meetingId);
	
	assert (stateBefore == isStarted() => (stateAfter == isStarted() || stateAfter ==isEnded())), "the status of the meeting changed from STARTED to an invalid state";
	assert ((stateBefore == isStarted() && stateAfter ==isEnded()) => f.selector == sig:endMeeting(uint256).selector), "the status of the meeting changed from STARTED to ENDED through a function other then endMeeting()";
}


// Checks that state transition from PENDING to STARTED or CANCELLED can only happen if
// startMeeting() or cancelMeeting() were called, respectively
// @note read again the comment at the top regarding f.selector
rule checkPendingToCancelledOrStarted(method f, uint256 meetingId) {

	env e; 
	calldataarg arg;

	IMeetingScheduler.MeetingStatus stateBefore = getStateById(meetingId);

	f(e, arg);

	IMeetingScheduler.MeetingStatus stateAfter = getStateById(meetingId);

	assert stateBefore == isPending() => (stateAfter == isPending() || stateAfter == isCancelled() || stateAfter == isStarted()), "StateAfter must be PENDING, STARTED or CANCLED";


	assert (stateBefore == isPending() && (stateAfter == isCancelled() )) => f.selector == sig:cancelMeeting(uint256).selector , "State to CANCLED must be changed by cancleMeeting()";

	assert (stateBefore == isPending() && stateAfter == isStarted()) => (f.selector == sig:startMeeting(uint256).selector), "State to STARTED must be changed by startMeeting()";
}


// Checks that the number of participants in a meeting cannot be decreased
rule monotonousIncreasingNumOfParticipants(method f, env e, calldataarg arg, uint256 meetingId) {

	require getStateById(meetingId) == isUninitalized() => getnumOfParticipants(meetingId) == 0; 

	mathint numBefore = getnumOfParticipants(meetingId);

	f(e, arg);

	mathint numAfter = getnumOfParticipants(meetingId);

	assert numAfter >= numBefore, "Number of participenst need to increase or stay the same";

}
