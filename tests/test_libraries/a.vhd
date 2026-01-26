
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

library b_lib;
library c_lib;

entity a is
  port (
    clk   : in std_logic;
    reset : in std_logic
  );
end entity;

architecture rtl of a is

begin

  i_b : entity b_lib.b
  port map (
    clk => clk,
    reset => reset
  );

  i_c : entity c_lib.c
  port map (
    clk => clk,
    reset => reset
  );

  process (clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        null;
      end if;
    end if;
  end process;

end architecture;