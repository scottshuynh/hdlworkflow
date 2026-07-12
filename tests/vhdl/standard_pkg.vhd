--------------------------------------------------------------------------------
-- Standard utility functions.
--------------------------------------------------------------------------------

library ieee;
  use ieee.std_logic_1164.all;
  use ieee.numeric_std.all;

package standard_pkg is

  function is_sim return boolean;
  function ceil_divide (n : natural; d : natural) return natural;
  function ceil_log2 (num : natural) return natural;
  function is_odd (num : natural) return boolean;
  function is_even (num : natural) return boolean;
  function shift_left (slv : std_logic_vector; num_shift : natural) return std_logic_vector;
  function shift_right (slv : std_logic_vector; num_shift : natural) return std_logic_vector;
  function gray2bin (gray : std_logic_vector) return unsigned;
  function bin2gray (bin : unsigned) return std_logic_vector;
  function to_slv (num : integer; slv_w : natural) return std_logic_vector;
  function to_unsigned (sl : std_logic) return unsigned;
  function resize (slv : std_logic_vector; slv_w : natural) return std_logic_vector;
  function zeros (slv_w : natural) return std_logic_vector;
  function zeros (nun_w : natural) return unsigned;
  function zeros (nun_w : natural) return signed;

end package standard_pkg;

package body standard_pkg is

  function is_sim return boolean is
  begin
    -- pragma translate_off
    return TRUE;
    -- pragma translate_on
    return FALSE;
  end function is_sim;

  function ceil_divide (n : natural; d : natural) return natural is
    variable result : natural;
  begin
    result := (n + d - 1) / d;
    return result;
  end function ceil_divide;

  function ceil_log2 (num : natural) return natural is
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
  end function ceil_log2;

  function is_odd (num : natural) return boolean is
    variable result : boolean := false;
  begin
    if (num mod 2 = 1) then
      result := true;
    end if;

    return result;
  end function is_odd;

  function is_even (num : natural) return boolean is
    variable result : boolean := false;
  begin
    if (num mod 2 = 0) then
      result := true;
    end if;

    return result;
  end function is_even;

  function shift_left (slv : std_logic_vector; num_shift : natural) return std_logic_vector is
  begin
    return std_logic_vector(shift_left(unsigned(slv), num_shift));
  end function shift_left;

  function shift_right (slv : std_logic_vector; num_shift : natural) return std_logic_vector is
  begin
    return std_logic_vector(shift_right(unsigned(slv), num_shift));
  end function shift_right;

  function gray2bin (gray : std_logic_vector) return unsigned is
    variable result : unsigned(gray'length - 1 downto 0);
  begin
    for idx in 0 to gray'length - 1 loop

      result(IDX) := xor shift_right(gray, IDX);

    end loop;

    return result;
  end function gray2bin;

  function bin2gray (bin : unsigned) return std_logic_vector is
  begin
    return std_logic_vector(shift_right(bin, 1) xor bin);
  end function bin2gray;

  function to_slv (num : integer; slv_w : natural) return std_logic_vector is
  begin
    return std_logic_vector(to_signed(num, slv_w));
  end function to_slv;

  function to_unsigned (sl : std_logic) return unsigned is
    variable result : unsigned(0 downto 0);
  begin
    result(0) := sl;
    return result;
  end function to_unsigned;

  function resize (slv : std_logic_vector; slv_w : natural) return std_logic_vector is
    variable result : std_logic_vector(slv_w - 1 downto 0);
  begin
    result := std_logic_vector(resize(unsigned(slv), slv_w));
    return result;
  end function resize;

  function zeros (slv_w : natural) return std_logic_vector is
    variable result : std_logic_vector(slv_w - 1 downto 0) := (others => '0');
  begin
    return result;
  end function zeros;

  function zeros (nun_w : natural) return unsigned is
    variable result : unsigned(nun_w - 1 downto 0) := (others => '0');
  begin
    return result;
  end function zeros;

  function zeros (nun_w : natural) return signed is
    variable result : signed(nun_w - 1 downto 0) := (others => '0');
  begin
    return result;
  end function zeros;

end package body standard_pkg;
