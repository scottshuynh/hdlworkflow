--------------------------------------------------------------------------------
-- Write and read ports have same widths.
-- Writes take 1 clock cycles.
-- Reads take 1 + NUM_PIPELINE clock cycles.
--------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.standard_pkg.all;
use work.array_pkg.all;

entity ram_simple_dual_port is
  generic (
    DATA_W       : positive;
    ADDR_W       : positive;
    BYTE_W       : natural     := 8;
    NUM_PIPELINE : natural     := 1;
    INIT_RAM     : array_slv_t := NULL_ARRAY_SLV
  );
  port (
    clk_i         : in  std_logic;
    wr_ce_i       : in  std_logic := '1';
    wr_en_i       : in  std_logic_vector(ceil_divide(DATA_W, BYTE_W)-1 downto 0);
    wr_addr_i     : in  unsigned(ADDR_W-1 downto 0);
    wr_data_i     : in  std_logic_vector(DATA_W-1 downto 0);
    rd_ce_i       : in  std_logic := '1';
    rd_addr_i     : in  unsigned(ADDR_W-1 downto 0);
    rd_data_o     : out std_logic_vector(DATA_W-1 downto 0);
    rd_data_vld_o : out std_logic
  );
end entity ram_simple_dual_port;

architecture rtl of ram_simple_dual_port is
  constant BYTE_EN_W  : natural := ceil_divide(DATA_W, BYTE_W);
  constant RD_LATENCY : natural := 1 + NUM_PIPELINE;

  -- If `arr` is a NULL array, returns array of zeros, otherwise returns `arr`.
  function initialise_ram (arr : array_slv_t) return array_slv_t is
    variable result : array_slv_t(0 to 2**ADDR_W-1)(DATA_W-1 downto 0);
  begin
    if (arr'left > arr'right) then
      result := (others => (others => '0'));
    else
      result := arr;
    end if;
    return result;
  end function;

  function get_cumsum_byte_widths(byte_width : natural) return array_integer_t is
    variable result : array_integer_t(0 to BYTE_EN_W-1);
  begin
    l_cumsum : for IDX in result'range loop
      if IDX = 0 then
        if BYTE_W > DATA_W then
          result(IDX) := DATA_W;
        else
          result(IDX) := BYTE_W;
        end if;
      else
        if IDX*BYTE_W > DATA_W then
          result(IDX) := DATA_W;
        else
          result(IDX) := result(IDX-1) + BYTE_W;
        end if;
      end if;
    end loop;
    return result;
  end function;

  function write_strobe (data : std_logic_vector(DATA_W-1 downto 0); byte_en : std_logic_vector(BYTE_EN_W-1 downto 0)) return std_logic_vector is
    constant WIDTHS       : array_integer_t                                  := get_cumsum_byte_widths(BYTE_W);
    constant DATA_RESIZED : std_logic_vector(WIDTHS(WIDTHS'high)-1 downto 0) := resize(data, WIDTHS(WIDTHS'high));
    variable result       : std_logic_vector(WIDTHS(WIDTHS'high)-1 downto 0);
  begin
    l_byte_en : for IDX in byte_en'range loop
      if (byte_en(IDX) = '1') then
        if IDX = 0 then
          result(WIDTHS(IDX)-1 downto 0) := DATA_RESIZED(WIDTHS(IDX)-1 downto 0);
        else
          result(WIDTHS(IDX)-1 downto WIDTHS(IDX-1)) := DATA_RESIZED(WIDTHS(IDX)-1 downto WIDTHS(IDX-1));
        end if;
      end if;
    end loop;
    return result;
  end function;

  signal ram           : array_slv_t(0 to 2**ADDR_W-1)(DATA_W-1 downto 0)  := initialise_ram(INIT_RAM);
  signal z_rd_data     : array_slv_t(0 to NUM_PIPELINE)(DATA_W-1 downto 0) := (others => (others => '0'));
  signal z_rd_data_vld : std_logic_vector(NUM_PIPELINE downto 0)           := (others => '0');
begin
  -- Writing to RAM takes 1 clock cycle.
  p_write : process (clk_i)
  begin
    if rising_edge(clk_i) then
      if (wr_ce_i = '1') then
        if (or wr_en_i = '1') then
          ram(to_integer(wr_addr_i)) <= write_strobe(wr_data_i, wr_en_i)(DATA_W-1 downto 0);
        end if;
      end if;
    end if;
  end process;

  -- Reading from RAM takes at least 1 clock cycles.
  -- When NUM_PIPELINE > 0, fabric LUTs are used to register output.
  p_read : process (clk_i)
  begin
    if rising_edge(clk_i) then
      if (rd_ce_i = '1') then
        z_rd_data(0)     <= ram(to_integer(rd_addr_i));
        z_rd_data_vld(0) <= '1';
      else
        z_rd_data_vld(0) <= '0';
      end if;

      if NUM_PIPELINE > 0 then
        l_rd_data : for IDX in 1 to NUM_PIPELINE loop
          z_rd_data(IDX)     <= z_rd_data(IDX-1);
          z_rd_data_vld(IDX) <= z_rd_data_vld(IDX-1);
        end loop;
      end if;
    end if;
  end process;

  rd_data_o     <= z_rd_data(z_rd_data'high);
  rd_data_vld_o <= z_rd_data_vld(z_rd_data_vld'high);

end architecture;
