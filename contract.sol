pragma solidity ^0.4.19;

contract metaData {
    string public DBdata;
    function metaData() {
        DBdata = 'Hi leee';
    }
    function setDBdata(string _DBdata) public {
        DBdata = _DBdata;
    }
    function getDBdata() constant returns (string) {
        return DBdata;
    }
}
