
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

library d_lib;

entity c is
  port (
    clk   : in std_logic;
    reset : in std_logic
  );
end entity;

architecture rtl of c is
begin

  i_d : entity d_lib.d
  port map (
    clk => clk,
    reset => reset
  );

end architecture;