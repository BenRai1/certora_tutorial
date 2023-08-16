/***
 * # ERC20 Example
 *
 * This is an example specification for a generic ERC20 contract.
 * 
 * To simulate the execution of all functions in the main contract, 
 *		you can define a method argument in the rule and use it in a statement.
 *		Run:
 *		 	certoraRun ERC20.sol --verify ERC20:Parametric.spec --solc solc8.0 --msg "parametric rule"
 * 
 */

methods {
    // When a function is not using the environment (e.g., msg.sender), it can be declared as envfree 
    function balanceOf(address) external returns(uint) envfree;
    function allowance(address,address) external returns(uint) envfree;
    function totalSupply() external returns(uint) envfree;
}


//// ## Part 2: parametric rules ///////////////////////////////////////////////

/// If `approve` changes a holder's allowance, then it was called by the holder
rule onlyHolderCanChangeAllowance {
    address holder; address spender;

    mathint allowance_before = allowance(holder, spender);

    method f; env e; calldataarg args; 
    f(e, args);                        

    mathint allowance_after = allowance(holder, spender);

    assert allowance_after > allowance_before => e.msg.sender == holder,
        "approve must only change the sender's allowance";

    assert allowance_after > allowance_before =>
        (f.selector == sig:approve(address,uint).selector || f.selector == sig:increaseAllowance(address,uint).selector || f.selector == sig:decreaseAllowance(address,uint).selector),
        "only approve and increaseAllowance can increase allowances";
}


/// If the balance of a user decreases the the user was msg.sender 

rule onlyHolderCanDecreaseBalance(method f)
filtered{
        f-> f.selector != sig:transferFrom(address,address,uint256).selector
    }{
    
    env e; 
    address owner; 
     
    calldataarg arg;
    address sender;
    address recipient;
    uint256 amount;

    uint256 balanceBefore = balanceOf(owner);

    if (f.selector == sig:transferFrom(address,address,uint256).selector ){
        assert allowance(owner, e.msg.sender) == 0;
        transferFrom(e, sender, recipient, amount);

    }
    f(e, arg);

    uint256 balanceAfter = balanceOf(owner);
    
    assert balanceBefore > balanceAfter => e.msg.sender == owner, "Only owner can reduce his balance";
}

