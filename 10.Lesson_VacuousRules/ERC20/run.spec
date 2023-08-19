
rule MethodsVacuityCheck(method f, env e, calldataarg arg){

    f(e, arg);
    assert false, "The methode should have a non reverting path";

}