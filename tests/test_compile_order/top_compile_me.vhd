library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.env.finish;

entity top_compile_me is
end entity;

architecture rtl of top_compile_me is
  signal clk_i : std_logic := '1';
  signal rst_i : std_logic := '1';
  signal ce_i  : std_logic := '1';
  
begin

  clk_i <= not clk_i after 1 ns;
  rst_i <= '0' after 10 ns;

  i_compile_0 : entity work.compile_me_0
    port map
    (
      clk_i => clk_i,
      rst_i => rst_i,
      ce_i  => ce_i
    );

  i_compile_me_1 : entity work.compile_me_1
    port map
    (
      clk_i => clk_i,
      rst_i => rst_i,
      ce_i  => ce_i
    );

  process
  begin
    wait for 128 ns;
    finish;
  end process;

end architecture;