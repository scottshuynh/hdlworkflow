--------------------------------------------------------------------------------
-- Type definitions and utility functions for arrays.
--------------------------------------------------------------------------------

library ieee;
  use ieee.std_logic_1164.all;
  use ieee.numeric_std.all;

package array_pkg is

  type array_integer_t is array (natural range <>) of integer;

  type array_slv_t is array (natural range <>) of std_logic_vector;
  type array2_slv_t is array (natural range <>) of array_slv_t;

  type array_signed_t is array(natural range <>) of signed;

  type array_unsigned_t is array(natural range <>) of unsigned;
  type array2_unsigned_t is array (natural range <>) of array_unsigned_t;

  constant NULL_ARRAY_INTEGER  : array_integer_t(0 to -1)               := (others => 0);
  constant NULL_ARRAY_SLV      : array_slv_t(0 to -1)(-1 downto 0)      := (others => (others => '0'));
  constant NULL_ARRAY_SIGNED   : array_signed_t(0 to -1)(-1 downto 0)   := (others => (others => '0'));
  constant NULL_ARRAY_UNSIGNED : array_unsigned_t(0 to -1)(-1 downto 0) := (others => (others => '0'));

  function zeros (arr_len : positive) return integer_vector;
  function zeros (arr_len : positive; slv_w : positive) return array_slv_t;
  function zeros (arr_len : positive; num_w : positive) return array_signed_t;
  function zeros (arr_len : positive; num_w : positive) return array_unsigned_t;
  function zeros (arr2_len : positive; arr1_len : positive; slv_w : positive) return array2_slv_t;

  function to_array_slv(slv : std_logic_vector; elem_w:positive) return array_slv_t;
  function to_array_signed (arr_int : array_integer_t; num_w : positive) return array_signed_t;

  function to_flat_slv(arr_slv : array_slv_t) return std_logic_vector;

  function resize(arr : array_slv_t; arr_len : natural) return array_slv_t;
  function resize(arr2 : array2_slv_t; arr_len2 : natural) return array2_slv_t;

end package array_pkg;

package body array_pkg is

  function zeros (arr_len : positive) return integer_vector is
    constant RESULT : integer_vector(0 to arr_len-1) := (others => 0);
  begin
    return RESULT;
  end function;

  function zeros (arr_len : positive; slv_w : positive) return array_slv_t is
    constant RESULT : array_slv_t(0 to arr_len - 1)(slv_w - 1 downto 0) := (others => (others => '0'));
  begin
    return RESULT;
  end function zeros;

  function zeros (arr_len : positive; num_w : positive) return array_signed_t is
    constant RESULT : array_signed_t(0 to arr_len - 1)(num_w - 1 downto 0) := (others => (others => '0'));
  begin
    return RESULT;
  end function zeros;

  function zeros (arr_len : positive; num_w : positive) return array_unsigned_t is
    constant RESULT : array_unsigned_t(0 to arr_len - 1)(num_w - 1 downto 0) := (others => (others => '0'));
  begin
    return RESULT;
  end function zeros;

  function zeros (arr2_len : positive; arr1_len : positive; slv_w : positive) return array2_slv_t is
    constant RESULT : array2_slv_t(0 to arr2_len-1)(0 to arr1_len-1)(slv_w-1 downto 0) := (others => (others => (others => '0')));
  begin
    return result;
  end function;

  function to_array_slv(slv : std_logic_vector; elem_w: positive) return array_slv_t is
    constant NUM_ELEMS : positive :=  slv'length / elem_w;
    variable result : array_slv_t(0 to NUM_ELEMS-1)(elem_w-1 downto 0) := zeros(NUM_ELEMS, elem_w);
  begin
    assert slv'length mod elem_w = 0
    report "Element width must be divisible by unpacked slv length"
    severity FAILURE;

    for idx in 0 to slv'length/elem_w-1 loop
      result(idx) := slv(elem_w*(idx+1)-1 downto elem_w*idx);
    end loop;
    return result;
  end function;

  function to_array_signed (arr_int : array_integer_t; num_w : positive) return array_signed_t is
    variable result : array_signed_t(arr_int'range)(num_w - 1 downto 0);
  begin
    l_elem : for idx in arr_int'range loop

      result(IDX) := to_signed(arr_int(IDX), num_w);

    end loop;

    return result;
  end function to_array_signed;

  function to_flat_slv(arr_slv : array_slv_t) return std_logic_vector is
    constant ELEM_W : positive := arr_slv(arr_slv'low)'length;
    constant FLAT_W : positive := arr_slv'length * ELEM_W;
    constant VIEW_ARR : array_slv_t(0 to arr_slv'length-1)(ELEM_W-1 downto 0) := arr_slv;
    variable result : std_logic_vector(FLAT_W-1 downto 0);
  begin
    for idx in VIEW_ARR'range loop
      result(ELEM_W*(idx+1)-1 downto ELEM_W*idx) := VIEW_ARR(idx);
    end loop;
    return result;
  end function;

  function resize(arr : array_slv_t; arr_len : natural) return array_slv_t is
    constant ELEM_W : natural := arr(arr'low)'length;
    constant VIEW_ARR : array_slv_t(0 to arr'length-1)(ELEM_W-1 downto 0) := arr;
    variable result : array_slv_t(0 to arr_len-1)(ELEM_W-1 downto 0) := zeros(arr_len, ELEM_W);
  begin
    for idx in VIEW_ARR'range loop
      result(idx) := VIEW_ARR(idx);
    end loop;
    return result;
  end function;

  function resize(arr2 : array2_slv_t; arr_len2 : natural) return array2_slv_t is
    constant arr1_len : natural := arr2(arr2'low)'length;
    constant elem_w : natural := arr2(arr2'low)(arr2(arr2'low)'low)'length;
    constant VIEW_ARR2 : array2_slv_t(0 to arr2'length)(0 to arr1_len-1)(elem_w-1 downto 0) := arr2;
    variable result : array2_slv_t(0 to arr_len2-1)(0 to arr1_len-1)(elem_w-1 downto 0) := zeros(arr_len2, arr1_len, elem_w);
  begin
    for idx in VIEW_ARR2'range loop
      result(idx) := VIEW_ARR2(idx);
    end loop;
    return result;
  end function;

end package body array_pkg;
