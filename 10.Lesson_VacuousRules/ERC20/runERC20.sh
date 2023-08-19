certoraRun ERC20Fixed.sol:ERC20 --verify ERC20:ERCVacuity.spec \
--send_only \
--optimistic_loop \
# --rule_sanity \
--msg "$1" \
--rule "transferOutDoesNotChangePowerBalance"