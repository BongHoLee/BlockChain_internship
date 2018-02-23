pragma solidity ^0.4.19;

contract MetaData {

  struct UserStruct {
    string userEmail;
    uint userAge;
    uint index;
  }

  mapping(uint => UserStruct) userStructs;
  string[] private data;


  function insertData(
   string _dbData)
    public
  {
    //if(isUser(userAddress)) revert();
    data.push(_dbData);

  }

  function getData(uint id)
    public
    constant
    returns(string dbData)
  {
    return(data[id]);
  }

  function getIndex()
    public
    constant
    returns(uint count)
  {
    return data.length - 1;
  }




}
