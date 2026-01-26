
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

entity d is
  port (
    clk   : in std_logic;
    reset : in std_logic
  );
end entity;

architecture rtl of d is
begin

  i_e : entity work.e
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