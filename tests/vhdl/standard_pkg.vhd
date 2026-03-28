--------------------------------------------------------------------------------
-- Standard utility functions.
--------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package standard_pkg is
  function is_sim return boolean;

  function ceil_divide(n : natural; d : natural) return natural;
  function ceil_log2(num : natural) return natural;

  function is_odd(num : natural) return boolean;
  function is_even(num : natural) return boolean;

  function shift_left(slv : std_logic_vector; num_shift : natural) return std_logic_vector;
  function shift_right(slv : std_logic_vector; num_shift : natural) return std_logic_vector;

  function gray2bin(gray : std_logic_vector) return unsigned;
  function bin2gray(bin : unsigned) return std_logic_vector;

  function to_slv(num : integer; slv_w : natural) return std_logic_vector;
  function to_unsigned(sl : std_logic) return unsigned;

  function resize(slv : std_logic_vector; slv_w : natural) return std_logic_vector;
end package;

package body standard_pkg is
  function is_sim return boolean is
  begin
    -- pragma translate_off
    return TRUE;
    -- pragma translate_on
    return FALSE;
  end function;

  function ceil_divide(n : natural; d : natural) return natural is
    variable result : natural;
  begin
    result := (n + d - 1) / d;
    return result;
  end function;

  function ceil_log2(num : natural) return natural is
    variable divide : natural := num;
    variable result : natural;
  begin
    l_divide : while (divide /= 1) loop
      divide := ceil_divide(divide, 2);
      if (divide >= 1) then
        result := result + 1;
      end if;  
    end loop;
    return result;
  end function;

  function is_odd(num : natural) return boolean is
    variable result : boolean := false;
  begin
    if (num mod 2 = 1) then
      result := true;
    end if;
    return result;
  end function;

  function is_even(num : natural) return boolean is
    variable result : boolean := false;
  begin
    if (num mod 2 = 0) then
      result := true;
    end if;
    return result;
  end function;

  function shift_left(slv : std_logic_vector; num_shift : natural) return std_logic_vector is
  begin
    return std_logic_vector(shift_left(unsigned(slv), num_shift));
  end function;
  
  function shift_right(slv : std_logic_vector; num_shift : natural) return std_logic_vector is
  begin
    return std_logic_vector(shift_right(unsigned(slv), num_shift));
  end function;

  function gray2bin(gray : std_logic_vector) return unsigned is
    variable result : unsigned(gray'length-1 downto 0);
  begin
    for IDX in 0 to gray'length-1 loop
      result(IDX) := xor shift_right(gray, IDX);
    end loop;
    return result;
  end function;

  function bin2gray(bin : unsigned) return std_logic_vector is
  begin
    return std_logic_vector(shift_right(bin, 1) xor bin);
  end function;

  function to_slv(num : integer; slv_w : natural) return std_logic_vector is
  begin
    return std_logic_vector(to_signed(num, slv_w));
  end function;

  function to_unsigned(sl : std_logic) return unsigned is
    variable result : unsigned(0 downto 0);
  begin
    result(0) := sl;
    return result;
  end function;

  function resize(slv : std_logic_vector; slv_w : natural) return std_logic_vector is
    variable result : std_logic_vector(slv_w-1 downto 0);
  begin
    result := std_logic_vector(resize(unsigned(slv), slv_w));
    return result;
  end function;
  
end package body;
