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

/// User can only use fransferFrom if they have allowance from the sender

rule transferFromOnlyWorksWithAllowance{
    env e; 
    address sender; 
    address recipient;
    uint256 amount;
    require amount > 0;

    uint256 allowanceBefore = allowance(sender, e.msg.sender);
    transferFrom(e, sender, recipient, amount);
    uint256 allowanceAfter = allowance(sender, e.msg.sender);

    assert allowanceBefore > 0, "Using transferFrom() only works if msg.sender has allowance";
}

/// When using transferFrom() the allowance of msg.sender should decrease by amount

rule transferFromReducesAllowance{
    env e;
    address sender; 
    address recipient;
    uint256 amount;

    mathint allowanceBefore = allowance(sender, e.msg.sender);
    transferFrom(e, sender, recipient, amount);
    mathint allowanceAfter = allowance(sender, e.msg.sender);

    assert allowanceAfter == allowanceBefore - amount, "Using transferFrom() must reduce allowance of msg.sender";
}


/// When using transferFrom() the balance of sender must decreas by amount and the balance of recipient should increase by amount 

rule transferFromReducesBalance{
    env e;
    address sender; 
    address recipient;
    require sender != recipient;
    uint256 amount;

    mathint balance_sender_before = balanceOf(sender);
    mathint balance_recipient_before = balanceOf(recipient);
    transferFrom(e, sender, recipient, amount);
    mathint balance_sender_after = balanceOf(sender);
    mathint balance_recipient_after = balanceOf(recipient);

    assert balance_sender_after == balance_sender_before - amount && balance_recipient_after == balance_recipient_before + amount, "Using transferFrom() must reduce balance of sender by amount and increase balance of recepient by amount";
}

/// When using transferFrom() must revert if the sender's balance is too small or the user does not have sufficant allowance


rule transferFromReverts{
    env e;
    address sender; 
    address recipient;
    require sender != recipient;
    uint256 amount;

    uint256 balanceSender = balanceOf(sender);
    uint256 allowanceMsgSender = allowance(sender, e.msg.sender);
    require balanceSender < amount || allowanceMsgSender < amount;

    
    transferFrom@withrevert(e, sender, recipient, amount);
   

    assert lastReverted, "Must revert if allowance or balance is to low";
}

/// transferFrom() must not revert if balance and allowance are higher than amount

rule transferFromDoesntRevert{
    env e;
    require e.msg.sender != 0;
    address sender; 
    require sender != 0;
    address recipient;
    require recipient != 0;
    uint256 amount;

    

    uint256 balanceSender = balanceOf(sender);
    mathint balanceRecipient = balanceOf(recipient);
    require balanceRecipient <= max_uint- 2 - amount; // to prevent overflow
    uint256 allowanceMsgSender = allowance(sender, e.msg.sender);
    require balanceSender >= amount && allowanceMsgSender >= amount && e.msg.value == 0;

    
    transferFrom@withrevert(e, sender, recipient, amount);
   

    assert !lastReverted, "Must not revert if allowance or balance are high enough";
}


//increase/decreasAllowance changes the allowance by the amount

rule increaseAlowance{
    env e;
    require e.msg.sender != 0;
    address spender; 
    // require sender != 0;
    uint256 amount;

    

    mathint allowance_before = allowance(e.msg.sender, spender);
   
    increaseAllowance(e, spender, amount);

    mathint allowance_after = allowance(e.msg.sender, spender);

    assert allowance_after == allowance_before + amount , "Must increase the allowance by amount";

}

rule decreaseAlowance{
    env e;
    require e.msg.sender != 0;
    address spender; 
    // require sender != 0;
    uint256 amount;

    

    mathint allowance_before = allowance(e.msg.sender, spender);
   
    decreaseAllowance(e, spender, amount);

    mathint allowance_after = allowance(e.msg.sender, spender);

    assert allowance_after == allowance_before - amount || allowance_after == 0, "Must reduce the allowance by amount";

}

/// only owner can mint

rule onlyOwnerCanMint{
 env e;
 uint256 amount;
 address to;

 mint(e, to, amount);

 assert e.msg.sender == _owner(e);

}

/// mint increases the total supply by amount and the balance of to address by amount

rule mintIncreasesSupplyAndBalance{
 env e;
 uint256 amount;
 address to;

 mathint balance_to_before = balanceOf(to);
 mathint totalSupplyBefore = _totalSupply(e);

 mint(e, to, amount);

 mathint balance_to_after = balanceOf(to);
 mathint totalSupplyAfter = _totalSupply(e);

 assert balance_to_after == balance_to_before + amount && totalSupplyAfter == totalSupplyBefore + amount;

}

/// only owner can burn

rule onlyOwnerCanBurn{
 env e;
 uint256 amount;
 address to;

 burn(e, to, amount);

 assert e.msg.sender == _owner(e);

}

/// burn decreases the total supply by amount and the balance of to address by amount

rule burnDecreasesSupplyAndBalance{
 env e;
 uint256 amount;
 address to;

 mathint balance_to_before = balanceOf(to);
 mathint totalSupplyBefore = _totalSupply(e);

 burn(e, to, amount);

 mathint balance_to_after = balanceOf(to);
 mathint totalSupplyAfter = _totalSupply(e);

 assert balance_to_after == balance_to_before - amount && totalSupplyAfter == totalSupplyBefore - amount;

}



