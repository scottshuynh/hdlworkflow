
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library std;
use std.env.finish;

library a_lib;

entity a_tb is
end entity;

architecture sim of a_tb is
  -- Clock period
  constant clk_period : time := 1 ns;
  -- Generics
  -- Ports
  signal clk   : std_logic := '0';
  signal reset : std_logic := '0';
  signal count : unsigned (3 downto 0) := (others => '0');
begin

  a_inst : entity a_lib.a
    port map
    (
      clk   => clk,
      reset => reset
    );
  clk <= not clk after clk_period/2;

  process (clk)
  begin
    if rising_edge(clk) then
      if and count = '1' then
        finish;
      else
        count <= count + 1;
      end if;
    end if;
  end process;

end architecture;